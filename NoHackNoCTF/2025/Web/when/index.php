<?php
date_default_timezone_set('Asia/Taipei');

$requestTime = date('Y-m-d H:i:s');

?>
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>When?</title>
    <link rel="icon" href="/file/favicon.ico" type="image/x-icon">
    <style>
        body {
            background: linear-gradient(135deg, #f8f9fa, #e0e0e0);
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            padding: 2rem 3rem;
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 {
            color: #333;
            margin-bottom: 0.5rem;
        }
        p {
            font-size: 1.2rem;
            color: #555;
            margin: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>When?</h1>
        <p><?php echo htmlspecialchars($requestTime); ?></p>
    </div>
</body>
</html>
