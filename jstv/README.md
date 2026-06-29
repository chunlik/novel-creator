# JSTV / CatPawOpen：饭搭子影视

這組檔案已部署到 `chunlik/novel-creator` 的 `jstv/` 目錄。

## 目錄結構

```text
jstv/
  js/
    fdzys.js
  dist/
    index.js
    index.js.md5
  gen_md5.py
```

## 目前可用連結

JSTV 訂閱連結：

```text
https://raw.githubusercontent.com/chunlik/novel-creator/refs/heads/main/jstv/dist/index.js.md5
```

站點 JS：

```text
https://raw.githubusercontent.com/chunlik/novel-creator/refs/heads/main/jstv/js/fdzys.js
```

## 說明

- `dist/index.js` 會把站點 `ext` 指向 `jstv/js/fdzys.js`
- `dist/index.js.md5` 是 `dist/index.js` 的 MD5
- 每次你改完 `dist/index.js`，要重新生成 `dist/index.js.md5`

## 重新生成 md5

```bash
cd jstv
python gen_md5.py
```
