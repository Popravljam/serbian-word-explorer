#!/bin/bash

SERVER="root@49.13.173.118"
DEPLOY_DIR="/opt/recnik"
WEB_DIR="/var/www/saptac-panel/recnik"

echo "🚀 Deploying Serbian Word Explorer to www.saptac.online/recnik"
echo ""

# Create deployment directory on server
echo "1. Creating directories on server..."
ssh $SERVER "mkdir -p $DEPLOY_DIR $WEB_DIR"

# Transfer application files
echo "2. Transferring application files..."
cd /Users/lazar/serbian-word-explorer

# Backend
scp -r backend/main.py backend/services backend/requirements.txt $SERVER:$DEPLOY_DIR/

# Frontend
scp -r frontend/* $SERVER:$WEB_DIR/

# Scripts
scp deploy.sh $SERVER:$DEPLOY_DIR/

echo "3. Transferring data repositories..."
# Transfer jezik
ssh $SERVER "mkdir -p $DEPLOY_DIR/jezik"
cd /Users/lazar/jezik
tar czf - lookup static templates | ssh $SERVER "cd $DEPLOY_DIR/jezik && tar xzf -"

# Transfer spisak-srpskih-reci
ssh $SERVER "mkdir -p $DEPLOY_DIR/spisak-srpskih-reci"
scp /Users/lazar/spisak-srpskih-reci/serbian-words.txt $SERVER:$DEPLOY_DIR/spisak-srpskih-reci/

# Transfer inflection-sr frequency data
ssh $SERVER "mkdir -p $DEPLOY_DIR/inflection-sr/data"
scp /Users/lazar/inflection-sr/data/word_frequency_table.tsv $SERVER:$DEPLOY_DIR/inflection-sr/data/

echo "4. Setting up Python environment on server..."
ssh $SERVER << 'ENDSSH'
cd /opt/recnik
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyyaml
ENDSSH

echo ""
echo "✅ Files transferred successfully!"
echo ""
echo "Next steps:"
echo "1. Configure systemd service"
echo "2. Configure nginx"
echo "3. Start the service"
