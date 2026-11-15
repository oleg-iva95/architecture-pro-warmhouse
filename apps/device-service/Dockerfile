FROM php:8.3-cli

RUN apt-get update && apt-get install -y --no-install-recommends \
        unzip git libpq-dev \
    && docker-php-ext-install pdo_pgsql \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /app
COPY . .

RUN composer install --no-dev --no-interaction --prefer-dist --optimize-autoloader

EXPOSE 8082

CMD ["php", "-S", "0.0.0.0:8082", "-t", "public"]
