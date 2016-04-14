# rabbitcasa

pip install puka
pip install simpledaemon
Optional: pip install blist

cd /opt/scripts/
git clone https://github.com/BlackMesh/rabbitcasa.git
ln -s /opt/scripts/rabbitcasa/init.d/rabbitcasa /etc/init.d/
cp rabbitcasa.conf.example /etc/rabbitcasa.conf
chkconfig rabbitcasa on
service rabbitcasa start
