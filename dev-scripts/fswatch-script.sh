if [ -z "$SSH_HOST" ]; then
  echo "Error: SSH_HOST environment variable is not set"
  exit 1
fi

# Test SSH connection
if ! ssh -q $SSH_HOST exit; then
  echo "Error: Cannot connect to $SSH_HOST. Please check the hostname and your SSH configuration"
  exit 1
fi


fswatch -0 ../ | while read -d "" event
do
  echo "Syncing..."
  rsync -avz ./ $SSH_HOST:~/rpi-long-range-video-transmission/
  echo "synced"
  echo "Restarting..."
  ssh $SSH_HOST "sudo systemctl restart video-transmission"
  echo "restarted"
done

