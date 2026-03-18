Remove-Item .git -Recurse -Force
git init
git lfs install
git lfs track "*.h5"
git add .gitattributes
git add .
git commit -m "clean production deployment commit"
git branch -M main
git remote add origin https://github.com/ankitt2005/KrushiSakha.git
git push -u origin main -f
