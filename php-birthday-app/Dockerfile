FROM php:8.2-apache

# Install SQLite CLI and ensure proper permissions
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY index.php /var/www/html/

# Configure Apache
RUN chown -R www-data:www-data /var/www/html \
    && a2enmod rewrite

EXPOSE 80