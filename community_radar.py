import requests
import csv
import datetime
import os
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

# Konfiguration
GITHUB_REPOS = {
    'Flutter': 'flutter/flutter',
    '.NET MAUI': 'dotnet/maui'
}

NUGET_PACKAGES = {
    '.NET MAUI': 'Microsoft.Maui.Controls'
}

CSV_DATEI = 'community_radar.csv'

def get_github_stars(repo):
    url = f'https://api.github.com/repos/{repo}'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('stargazers_count', 0)
    else:
        print(f'Fehler beim Abrufen von GitHub-Stars für {repo}: {response.status_code}')
        return None

def get_nuget_downloads(package_id):
    url = f'https://api.nuget.org/v3/registration5-semver1/{package_id.lower()}/index.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        versions = data.get('items', [])[0].get('items', [])
        if versions:
            total_downloads = sum(
                v['catalogEntry']['downloads'] for v in versions if 'catalogEntry' in v
            )
            return total_downloads
    print(f'Fehler beim Abrufen von NuGet-Downloads für {package_id}')
    return None

def schreibe_csv(zeile):
    datei_existiert = os.path.isfile(CSV_DATEI)
    with open(CSV_DATEI, mode='a', newline='', encoding='utf-8') as csv_datei:
        writer = csv.writer(csv_datei)
        if not datei_existiert:
            header = ['Datum', 'Flutter GitHub Stars', '.NET MAUI GitHub Stars', '.NET MAUI NuGet Downloads']
            writer.writerow(header)
        writer.writerow(zeile)

def erstelle_visualisierung():
    if not os.path.isfile(CSV_DATEI):
        print(f'Datei {CSV_DATEI} existiert nicht. Keine Visualisierung möglich.')
        return

    df = pd.read_csv(CSV_DATEI, parse_dates=['Datum'])
    df.sort_values('Datum', inplace=True)

    plt.figure(figsize=(12, 6))
    plt.plot(df['Datum'], df['Flutter GitHub Stars'], label='Flutter GitHub Stars', marker='o')
    plt.plot(df['Datum'], df['.NET MAUI GitHub Stars'], label='.NET MAUI GitHub Stars', marker='s')
    plt.plot(df['Datum'], df['.NET MAUI NuGet Downloads'], label='.NET MAUI NuGet Downloads', marker='^')

    plt.title('Community-Radar: Flutter vs. .NET MAUI')
    plt.xlabel('Datum')
    plt.ylabel('Anzahl')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Speichern der Visualisierung
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    dateiname = f'community_radar_visualisierung_{timestamp}.png'
    plt.savefig(dateiname)
    print(f'Visualisierung gespeichert als {dateiname}')

def main():
    heute = datetime.date.today().isoformat()
    flutter_stars = get_github_stars(GITHUB_REPOS['Flutter'])
    maui_stars = get_github_stars(GITHUB_REPOS['.NET MAUI'])
    maui_downloads = get_nuget_downloads(NUGET_PACKAGES['.NET MAUI'])

    if None not in (flutter_stars, maui_stars, maui_downloads):
        zeile = [heute, flutter_stars, maui_stars, maui_downloads]
        schreibe_csv(zeile)
        print(f'Daten für {heute} erfolgreich gespeichert.')
    else:
        print('Fehler beim Abrufen der Daten. CSV-Datei wurde nicht aktualisiert.')

    # Visualisierung erstellen
    erstelle_visualisierung()

if __name__ == '__main__':
    main()
