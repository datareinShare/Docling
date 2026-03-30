# Docling API 仕様書

## 概要

Docling API は、ドキュメント（PDF, DOCX, PPTX, HTML 等）を Markdown / プレーンテキスト / DocTags 形式に変換する REST API です。
IBM の [Docling](https://github.com/DS4SD/docling) ライブラリを FastAPI でラップしています。

- **ベースURL**: `https://<your-app>.up.railway.app`
- **プロトコル**: HTTPS
- **レスポンス形式**: JSON
- **Swagger UI**: `GET /docs`
- **ReDoc**: `GET /redoc`

---

## 認証

変換エンドポイント（`/convert/*`）は API キーによる認証が必要です。
`/health` は認証不要です。

### 設定方法

Railway の環境変数に `API_KEY` を設定してください。

```
API_KEY=your-secret-api-key
```

> **注意**: `API_KEY` が未設定の場合、認証はスキップされすべてのリクエストが許可されます。

### リクエスト方法

`X-API-Key` ヘッダーに API キーを含めてください。

```
X-API-Key: your-secret-api-key
```

### エラー

| ステータスコード | 説明 |
|---|---|
| 401 | API キーが未指定または不正 |

```json
{
  "detail": "Invalid or missing API key"
}
```

---

## 共通仕様

### 出力形式 (`format`)

各変換エンドポイントの `format` パラメータで出力形式を指定します。

| 値 | 説明 |
|---|---|
| `markdown` | Markdown 形式（デフォルト） |
| `text` | プレーンテキスト形式 |
| `doctags` | DocTags（Docling 独自のドキュメントトークン形式） |

### 対応ファイル形式（入力）

PDF, DOCX, PPTX, HTML, AsciiDoc, Markdown, CSV, XLSX 等
※ Docling がサポートする形式に準じます。

### エラーレスポンス

すべてのエンドポイントで共通のエラー形式を返します。

```json
{
  "detail": "エラーメッセージ"
}
```

| ステータスコード | 説明 |
|---|---|
| 401 | API キーが未指定または不正 |
| 400 | リクエスト不正（不正な base64、未対応の format 等） |
| 500 | サーバー内部エラー（変換処理の失敗等） |

---

## エンドポイント一覧

### 1. ヘルスチェック

サーバーの稼働状態を確認します。

```
GET /health
```

#### レスポンス

**200 OK**

```json
{
  "status": "ok"
}
```

---

### 2. URL から変換

指定した URL のドキュメントを取得して変換します。

```
POST /convert/url
```

#### リクエスト

**Content-Type**: `application/json`

| フィールド | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `url` | string | Yes | - | ドキュメントの URL |
| `format` | string | No | `"markdown"` | 出力形式 |

```json
{
  "url": "https://example.com/sample.pdf",
  "format": "markdown"
}
```

#### レスポンス

**200 OK**

```json
{
  "content": "# タイトル\n\n本文テキスト...",
  "format": "markdown"
}
```

---

### 3. Base64 データから変換

Base64 エンコードされたファイルデータを変換します。
Google Apps Script 等、ファイルアップロードが難しいクライアント向けです。

```
POST /convert/base64
```

#### リクエスト

**Content-Type**: `application/json`

| フィールド | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `data` | string | Yes | - | ファイルの Base64 エンコード文字列 |
| `filename` | string | Yes | - | ファイル名（拡張子を含むこと。例: `report.pdf`） |
| `format` | string | No | `"markdown"` | 出力形式 |

```json
{
  "data": "JVBERi0xLjQK...",
  "filename": "report.pdf",
  "format": "markdown"
}
```

#### レスポンス

**200 OK**

```json
{
  "content": "# タイトル\n\n本文テキスト...",
  "format": "markdown"
}
```

> **注意**: `filename` の拡張子は Docling がファイル形式を判定するために使用します。正しい拡張子を指定してください。

---

### 4. ファイルアップロードで変換

`multipart/form-data` でファイルを直接アップロードして変換します。

```
POST /convert/file
```

#### リクエスト

**Content-Type**: `multipart/form-data`

| フィールド | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `file` | file | Yes | - | アップロードするファイル |
| `format` | string | No | `"markdown"` | 出力形式 |

```bash
curl -X POST https://<your-app>.up.railway.app/convert/file \
  -F "file=@report.pdf" \
  -F "format=markdown"
```

#### レスポンス

**200 OK**

```json
{
  "content": "# タイトル\n\n本文テキスト...",
  "format": "markdown"
}
```

---

## 利用例

### curl

```bash
# URL から変換
curl -X POST https://<your-app>.up.railway.app/convert/url \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key" \
  -d '{"url": "https://example.com/sample.pdf"}'

# Base64 から変換
curl -X POST https://<your-app>.up.railway.app/convert/base64 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key" \
  -d '{"data": "JVBERi0xLjQK...", "filename": "sample.pdf"}'

# ファイルアップロード
curl -X POST https://<your-app>.up.railway.app/convert/file \
  -H "X-API-Key: your-secret-api-key" \
  -F "file=@sample.pdf" \
  -F "format=text"
```

### Google Apps Script

```javascript
var API_KEY = PropertiesService.getScriptProperties().getProperty("DOCLING_API_KEY");

function convertFromDrive() {
  var file = DriveApp.getFileById("YOUR_FILE_ID");
  var base64 = Utilities.base64Encode(file.getBlob().getBytes());

  var res = UrlFetchApp.fetch("https://<your-app>.up.railway.app/convert/base64", {
    method: "post",
    contentType: "application/json",
    headers: { "X-API-Key": API_KEY },
    payload: JSON.stringify({
      data: base64,
      filename: file.getName(),
      format: "markdown"
    })
  });

  var result = JSON.parse(res.getContentText());
  Logger.log(result.content);
}
```

> **GAS での API キー管理**: スクリプトエディタ → プロジェクトの設定 → スクリプトプロパティ に `DOCLING_API_KEY` を登録してください。

### Python

```python
import requests

res = requests.post(
    "https://<your-app>.up.railway.app/convert/url",
    headers={"X-API-Key": "your-secret-api-key"},
    json={"url": "https://example.com/sample.pdf", "format": "markdown"},
)
print(res.json()["content"])
```

---

## 制限事項

- リクエストボディのサイズ上限は Railway のプラン設定に依存します。
- 大きなファイルの変換は時間がかかる場合があります。GAS から呼び出す場合は 6 分の実行時間制限に注意してください。
- `API_KEY` 環境変数が未設定の場合、認証なしで全リクエストが許可されます。本番環境では必ず設定してください。
