<?php
session_start();

$data = [
    "2025/09/24" => "00ps, I should have sometime to contribute challenges right?\nBut I want to meet someone ...",
    "2025/10/03" => "Hmm... I forgot something but just can't remember them ;P",
    "2025/10/08" => "WTF, IS DEADLINE, FINE, THE FLAG IS QnQSec{test_flag_by_whale120}"
];

$search = $_POST['search'] ?? null;

if ($search) {
    $found = false;
    foreach ($data as $date => $content) {
        if (stripos($date, $search) !== false || stripos($content, $search) !== false) {
            $_SESSION['last_found_date'] = $date;
            session_destroy();
            break;
        }
    }
}

?>

<h1>Search Me</h1>
<h2><?php echo $search; ?></h2>
<form method="POST">
    <label>Search</label>
    <input type="text" name="search" required>
    <button type="submit">SEND!</button>
</form>
