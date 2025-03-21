<?php
header('Content-Type: application/json');

// Database setup
$db = new SQLite3('birthdays.db');
$db->exec('CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    date_of_birth DATE
)');

// Helper function to validate date
function isValidDate($dateStr) {
    $date = DateTime::createFromFormat('Y-m-d', $dateStr);
    return $date && $date->format('Y-m-d') === $dateStr;
}

// Parse request
$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH');
$method = $_SERVER['REQUEST_METHOD'];
$uriSegments = explode('/', trim($requestUri, '/'));

// Validate route structure
if (count($uriSegments) < 2 || $uriSegments[0] !== 'hello') {
    http_response_code(404);
    echo json_encode(['error' => 'Not found']);
    exit;
}

$username = $uriSegments[1];

// Validate username format
if (!preg_match('/^[a-zA-Z]+$/', $username)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid username format']);
    exit;
}

// Handle PUT request
if ($method === 'PUT') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['dateOfBrith'])) {
        http_response_code(400);
        echo json_encode(['error' => 'Missing dateOfBrith']);
        exit;
    }
    
    $dateStr = $input['dateOfBrith'];
    if (!isValidDate($dateStr)) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid date format']);
        exit;
    }
    
    $date = new DateTime($dateStr);
    $today = new DateTime();
    $today->setTime(0, 0, 0);
    
    if ($date >= $today) {
        http_response_code(400);
        echo json_encode(['error' => 'Date must be before today']);
        exit;
    }
    
    // Upsert user
    $stmt = $db->prepare('INSERT OR REPLACE INTO users VALUES (:user, :dob)');
    $stmt->bindValue(':user', $username, SQLITE3_TEXT);
    $stmt->bindValue(':dob', $dateStr, SQLITE3_TEXT);
    $stmt->execute();
    
    http_response_code(204);
    exit;
}

// Handle GET request
if ($method === 'GET') {
    $stmt = $db->prepare('SELECT date_of_birth FROM users WHERE username = :user');
    $stmt->bindValue(':user', $username, SQLITE3_TEXT);
    $result = $stmt->execute();
    $user = $result->fetchArray(SQLITE3_ASSOC);
    
    if (!$user) {
        http_response_code(404);
        echo json_encode(['error' => 'User not found']);
        exit;
    }
    
    $dob = new DateTime($user['date_of_birth']);
    $today = new DateTime();
    $today->setTime(0, 0, 0);
    
    // Calculate next birthday
    $currentYear = (int)$today->format('Y');
    $nextBirthday = DateTime::createFromFormat('Y-m-d', "$currentYear-".$dob->format('m-d'));
    
    if (!$nextBirthday || $nextBirthday < $today) {
        $nextBirthday = new DateTime($dob->format('m-d') . ' next year');
    }
    
    $interval = $today->diff($nextBirthday);
    $days = $interval->days;
    
    // Handle same day case
    if ($days === 0 && $nextBirthday->format('m-d') === $today->format('m-d')) {
        $message = "Hello, $username! Happy birthday!";
    } else {
        $message = "Hello, $username! Your birthday is in $days day(s)";
    }
    
    echo json_encode(['message' => $message]);
    exit;
}

// Handle other methods
http_response_code(405);
echo json_encode(['error' => 'Method not allowed']);