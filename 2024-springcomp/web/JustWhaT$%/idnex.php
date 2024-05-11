<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Calculator</title>
<style>
body, html {
  height: 100%;
  margin: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.input-box {
  width: 100px;
  padding: 10px;
  margin: 0 5px;
}
.button {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.button:hover {
  background-color: #45a049;
}

.button:active {
  background-color: #3e8e41;
  transform: translateY(2px);
}
</style>
</head>
<body>
<!---
<?php if(isset($_POST['input1'])&&isset($_POST['input1'])){eval("echo (".$_POST['input1']."+".$_POST['input2'].");");} ?>
--->
<form action="/calculate.php" method="POST" style="text-align: center;">
  <input type="string" name="input1" class="input-box">
  <span style="font-size: 24px;">+</span>
  <input type="string" name="input2" class="input-box">
  <button type="submit" class="button">计算</button>
<br></br>
<h1>Result : <?php if(isset($_POST['input1'])&&isset($_POST['input1'])){eval("echo (".$_POST['input1']."+".$_POST['input2'].");");} ?></h1>
</form>
</body>
</html>
