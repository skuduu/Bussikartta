#!/bin/sh

# Date format for backup file name
DATE=$(date +"%Y%m%d-%H%M%S")

# Full PostgreSQL data directory backup
tar czvf /backups/pgdata-backup-$DATE.tar.gz -C /var/lib/postgresql/data .

# Optional: keep only last 7 backups
cd /backups
ls -1tr | head -n -7 | xargs rm -f --

echo "Backup completed at $DATE"