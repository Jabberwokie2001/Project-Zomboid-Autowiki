yaml
name: Project Zomboid AutoWiki Pipeline
on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 0'
permissions:
  contents: write
jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install Dependencies
        run: pip install google-generativeai requests mkdocs-material
      - name: Execute Script
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python autowiki_core.py
      - name: Deploy Site
        run: |
          git config --global user.name "USAG-AutoWiki-Bot"
          git config --global user.email "bot@autowiki.local"
          mkdocs gh-deploy --force