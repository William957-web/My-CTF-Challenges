<?php
session_start();

// QwQ Nginx
$hostname = gethostname();
$server_ip = gethostbyname($hostname);
$client_ip = $_SERVER['HTTP_X_FORWARDED_FOR'];

$valid_token = 'REDACTED_TOKEN';

if ($client_ip === $server_ip) {
    $_SESSION['token'] = $valid_token;
    $token_message = "あなたのトークン: $valid_token";
} else {
    $token_message = "アクセス拒否";
}

// Form
$curl_result = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $url = $_POST['url'] ?? '';
    $send_token = $_POST['send_token'] ?? '';
    $token_input = $_POST['token_input'] ?? '';

    if (!empty($url)) {
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        // curl_setopt($ch, CURLOPT_HEADER, true);
        $response = curl_exec($ch);
        $error = curl_error($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        // curl_close($ch);

        if ($send_token && $token_input === $valid_token) {
            $curl_result = "<pre>" . htmlspecialchars($response) . "</pre>";
        } else {
            if ($error) {
                $curl_result = "接続失敗: " . htmlspecialchars($error);
            } else {
                $curl_result = "接続成功 (HTTPステータスコード: $http_code)";
            }
        }
    }
}
?>
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>接続テスト</title>
  <style>
    body {
      background: url('/static/background.jpg') center/cover no-repeat;
      min-height:100vh;
      display:flex;
      align-items:center;
      justify-content:center;
      margin:0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans TC", "Helvetica Neue", Arial;
      color:#222;
    }
    body::before{
      content:"";
      position:fixed;left:0;top:0;width:100%;height:100%;
      background: rgba(0,0,0,0.45);
      z-index:0;
    }
    .container{
      position:relative; z-index:1;
      width:900px; max-width:95%;
      background: linear-gradient(180deg, rgba(253,245,230,0.98), #ffffff);
      padding:28px; border-radius:12px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    }
    h1 {margin:0 0 6px 0; font-size:22px;}
    .subtitle {font-size:14px; color:#333; margin-bottom:8px;}
    .meta {font-size:13px; color:#666;}
    form .row {margin:12px 0; display:flex; gap:12px; flex-wrap:wrap;}
    label {display:block; font-size:13px; margin-bottom:6px;}
    input[type="text"], input[type="email"], textarea, select {
      width:100%;
      padding:10px; border:1px solid #ccc; border-radius:6px;
      font-size:14px; box-sizing:border-box;
    }
    textarea {min-height:100px; resize:vertical;}
    .col {flex:1 1 300px; min-width:220px;}
    .actions {text-align:right; margin-top:8px;}
    button {background:#1f8cff;color:white;padding:10px 16px;border-radius:8px;border:0;cursor:pointer;}
    .small-muted {font-size:12px;color:#666;margin-top:6px}
    .logo {max-width:120px; display:block; margin-bottom:12px;}
  </style>
</head>
<body>
  <div class="container">
    <h1>接続テスト</h1>
    <div class="subtitle"><?= htmlspecialchars($token_message) ?></div>
    <form method="post">
      <div class="row">
        <div class="col">
          <label for="url">URL</label>
          <input type="text" id="url" name="url" placeholder="https://example.com">
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label>
            <input type="checkbox" name="send_token" value="1"> 送信トークン
          </label>
        </div>
        <div class="col">
          <label for="token_input">トークン (必要な場合)</label>
          <input type="text" id="token_input" name="token_input">
        </div>
      </div>
      <div class="actions">
        <button type="submit">送信</button>
      </div>
    </form>
    <div class="small-muted"><?= $curl_result ?></div>
  </div>
</body>
</html>
