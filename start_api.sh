# Check if PSQL dtabase is running
PSQL_STATUS="$(systemctl is-active postgresql.service)"
if [ "${PSQL_STATUS}" = "active" ]; then
	echo 'PSQL service is running...'
else
	echo 'Starting PSQL service'
	systemctl start postgresql
fi

# Ensure pip requirements are up to date
echo 'Ensuring python packages are up to date...'
pip install -r requirements.txt > .start_api_pip.log
echo 'Starting SentiSounds API...' 
python3 backend/src/main.py
