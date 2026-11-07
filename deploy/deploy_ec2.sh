#!/usr/bin/env bash
# ==============================================================================
# Script de Despliegue Automatizado para PetCare en AWS EC2 (Ubuntu 22.04 / 24.04)
# Evaluación Parcial N°3 - Desarrollo Backend (INACAP)
# ==============================================================================

set -e

echo "=========================================================="
echo "🐾 Iniciando despliegue de PetCare en AWS EC2 con PostgreSQL"
echo "=========================================================="

APP_DIR="/home/ubuntu/petcare"
DB_NAME="petcare_db"
DB_USER="petcare_user"
DB_PASS="PetCarePass2026!"

# 1. Actualización de paquetes
echo ">> [1/8] Actualizando paquetes del sistema..."
sudo apt update -y
sudo apt upgrade -y

# 2. Instalación de dependencias del sistema y PostgreSQL
echo ">> [2/8] Instalando Python 3, PostgreSQL, Nginx y utilidades..."
sudo apt install -y python3-pip python3-venv python3-dev \
    libpq-dev postgresql postgresql-contrib nginx curl git

# 3. Configuración de Base de Datos PostgreSQL
echo ">> [3/8] Configurando base de datos PostgreSQL..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER'" | grep -q 1 || \
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'America/Santiago';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

# 4. Configurar Entorno Virtual Python
echo ">> [4/8] Configurando virtualenv e instalando dependencias..."
cd "$APP_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 5. Generar archivo .env para Producción
echo ">> [5/8] Configurando variables de entorno (.env)..."
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || echo "*")

cat <<EOF > .env
DEBUG=False
SECRET_KEY=petcare-prod-aws-ec2-key-$(openssl rand -hex 16)
ALLOWED_HOSTS=$PUBLIC_IP,localhost,127.0.0.1,*

# PostgreSQL en AWS EC2
USE_POSTGRES=True
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASS
DB_HOST=localhost
DB_PORT=5432
EOF

# 6. Migraciones, Seed Data y Collectstatic
echo ">> [6/8] Ejecutando migraciones ORM y poblando datos de prueba..."
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput

# 7. Configuración de Gunicorn como Servicio Systemd
echo ">> [7/8] Configurando servicio Gunicorn..."
sudo cp deploy/gunicorn.service /etc/systemd/system/petcare.service
sudo systemctl daemon-reload
sudo systemctl start petcare
sudo systemctl enable petcare

# 8. Configuración de Nginx
echo ">> [8/8] Configurando proxy inverso Nginx..."
sudo cp deploy/petcare_nginx.conf /etc/nginx/sites-available/petcare
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/petcare /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo "=========================================================="
echo "🎉 ¡DESPLIEGUE COMPLETADO CON ÉXITO EN AWS EC2!"
echo "Acceso web público disponible en:"
echo "http://$PUBLIC_IP/"
echo "Django Admin: http://$PUBLIC_IP/admin/"
echo "API REST DRF: http://$PUBLIC_IP/api/"
echo "Credenciales: admin / admin1234"
echo "=========================================================="
