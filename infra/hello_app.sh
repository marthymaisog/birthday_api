#!/bin/bash

# Configuration
DB_HOST="localhost"
DB_USERNAME="root"
DB_PASSWORD=""
DB_NAME="hello_app"

# Function to update user data
update_user_data() {
  local username=$1
  local date_of_birth=$2

  # Check if the username exists
  if mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD $DB_NAME -e "SELECT * FROM users WHERE username = '$username'" | grep -q "$username"; then
    # Update the user data
    mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD $DB_NAME -e "UPDATE users SET date_of_birth = '$date_of_birth' WHERE username = '$username'"
  else
    # Insert the user data
    mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD $DB_NAME -e "INSERT INTO users (username, date_of_birth) VALUES ('$username', '$date_of_birth')"
  fi
}

# Function to get the birthday message
get_birthday_message() {
  local username=$1

  # Get the user data
  local date_of_birth=$(mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD $DB_NAME -e "SELECT date_of_birth FROM users WHERE username = '$username'" | awk '{print $2}')

  if [ -n "$date_of_birth" ]; then
    # Calculate the days until the birthday
    local today=$(date +%s)
    local birthday=$(date -d "$date_of_birth" +%s)
    local days_until_birthday=$(( (birthday - today) / 86400 ))

    if [ $days_until_birthday -lt 0 ]; then
      birthday=$(date -d "next year $date_of_birth" +%s)
      days_until_birthday=$(( (birthday - today) / 86400 ))
    fi

    # Return the birthday message
    if [ $days_until_birthday -eq 0 ]; then
      echo "Hello, $username! Happy birthday!"
    else
      echo "Hello, $username! Your birthday is in $days_until_birthday day(s)"
    fi
  else
    echo "User not found"
  fi
}

# API Endpoints
while true; do
  read -r line
  case $line in
    PUT*)
      username=$(echo "$line" | cut -d '/' -f 3)
      date_of_birth=$(echo "$line" | cut -d ' ' -f 2 | cut -d '=' -f 2)
      update_user_data "$username" "$date_of_birth"
      echo "HTTP/1.1 204 No Content"
      ;;
    GET*)
      username=$(echo "$line" | cut -d '/' -f 3)
      message=$(get_birthday_message "$username")
      echo "HTTP/1.1 200 OK"
      echo "Content-Type: text/plain"
      echo ""
      echo "$message"
      ;;
    *)
      echo "HTTP/1.1 405 Method Not Allowed"
      ;;
  esac
done
