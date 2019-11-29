#!/bin/bash
source venv/bin/activate
flask run&
deactivate
cd ~/dev/react/pairup
npm start&
