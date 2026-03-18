git lfs install
git lfs track "*.h5"
git add .gitattributes
git add .
git commit -m "Initialize deployment ready code with LFS tracking"
git remote remove origin
git remote add origin https://github.com/ankitt2005/KrushiSakha.git
git branch -M main
git push -u origin main
