#!/usr/bin/env bash
# Génère le zip de rendu OC : Mettez_en_place_un_agent_IA_Hugou_Richard.zip
# Nommage interne : Hugou_Richard_<n>_<libellé>_082026.<ext>
# Rejouable : convertit les .md en PDF (markdown → HTML → Chrome headless), archive le code
# depuis git (develop), inclut la vidéo de démo si présente dans livrables/rendu/ (*demo*.mp4|mov|webm).
set -euo pipefail
cd "$(dirname "$0")/.."   # racine du dépôt

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
STAGE="livrables/rendu/zip-staging"
ZIP="livrables/rendu/Mettez_en_place_un_agent_IA_Hugou_Richard.zip"
rm -rf "$STAGE" "$ZIP" && mkdir -p "$STAGE"

md_vers_pdf() {  # $1 = source .md · $2 = destination .pdf
  local html="$STAGE/tmp.html"
  uv run --project backend --with markdown python3 - "$1" "$html" <<'PY'
import sys
import markdown
corps = markdown.markdown(open(sys.argv[1], encoding="utf-8").read(),
                          extensions=["tables", "fenced_code"])
style = """<meta charset="utf-8"><style>
@page { size: A4; margin: 18mm; }
body { font-family: "Helvetica Neue", Arial, sans-serif; color: #1c1b18; line-height: 1.5;
       font-size: 11.5pt; max-width: 100%; }
h1 { font-size: 19pt; margin: 0 0 12pt; } h2 { font-size: 14.5pt; margin: 16pt 0 8pt; color: #3a5a40; }
h3 { font-size: 12.5pt; margin: 12pt 0 6pt; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 10.5pt; }
th, td { border: 1px solid #bdb6a8; padding: 4pt 7pt; text-align: left; vertical-align: top; }
th { background: #f3eee4; }
code, pre { font-family: Menlo, monospace; font-size: 9.5pt; background: #f3eee4; }
pre { padding: 8pt; border-radius: 4pt; white-space: pre-wrap; }
blockquote { border-left: 3px solid #3a5a40; margin: 8pt 0; padding: 2pt 10pt; color: #4a4740; }
li { margin-bottom: 3pt; }
</style>"""
open(sys.argv[2], "w", encoding="utf-8").write(style + corps)
PY
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$2" "file://$PWD/$html" 2>/dev/null
  rm -f "$html"
  echo "  ✓ $(basename "$2")"
}

echo "── 1. Le code (archive git de develop) ──"
git archive --format=zip -o "$STAGE/Hugou_Richard_1_code_082026.zip" develop
printf "Dépôt public : https://github.com/richardhugou/p13-agent-ia-echecs (branche develop)\nDémarrage : ./demarrer.sh — voir README.md\n" > "$STAGE/Hugou_Richard_1_code_lien_depot.txt"
echo "  ✓ code + lien dépôt"

echo "── 2. La présentation ──"
cp livrables/rendu/presentation-soutenance.pdf "$STAGE/Hugou_Richard_2_presentation_082026.pdf"
echo "  ✓ présentation (13 diapos + annexes)"

echo "── 3-7. Les documents (md → PDF) ──"
md_vers_pdf livrables/note-benefices-limites.md   "$STAGE/Hugou_Richard_3_note_analyse_video_082026.pdf"
md_vers_pdf livrables/etude-faisabilite-couts.md  "$STAGE/Hugou_Richard_4_etude_faisabilite_couts_082026.pdf"
md_vers_pdf livrables/schema-architecture-mcp.md  "$STAGE/Hugou_Richard_5_schema_architecture_mcp_082026.pdf"
md_vers_pdf livrables/fiche-autoevaluation.md     "$STAGE/Hugou_Richard_6_fiche_autoevaluation_082026.pdf"
md_vers_pdf livrables/documentation-technique.md  "$STAGE/Hugou_Richard_7_documentation_technique_082026.pdf"

echo "── 8. La vidéo de démo (si présente) ──"
video=$(find livrables/rendu -maxdepth 1 -iname "*demo*.mp4" -o -iname "*demo*.mov" -o -iname "*demo*.webm" 2>/dev/null | head -1)
if [ -n "$video" ]; then
  cp "$video" "$STAGE/Hugou_Richard_8_video_demo_082026.${video##*.}"
  echo "  ✓ vidéo : $(basename "$video")"
else
  echo "  ⚠️  aucune vidéo *demo*.mp4/mov/webm dans livrables/rendu/ — à déposer puis relancer"
fi

echo "── Assemblage ──"
(cd "$STAGE" && zip -q -X "../$(basename "$ZIP")" ./*)
rm -rf "$STAGE"
echo "✅ $(du -h "$ZIP" | cut -f1) → $ZIP"
unzip -l "$ZIP" | tail -n +4 | head -12
