
Running npm run deploy
```
Creating an optimized production build...
Failed to compile.

Error: EACCES: permission denied, open '/Users/clarkngo/.config/svgrrc'
```
Solution: 
```
sudo chmod 755 ~/.config
```
