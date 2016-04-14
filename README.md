# rabbitcasa

### Package Dependencies
* pip install puka
* pip install simpledaemon
* Optional: pip install blist

### Starting the service
Make sure to edit the /etc/rabbitcasa.conf below.
```
cd /opt/scripts/
git clone https://github.com/BlackMesh/rabbitcasa.git
ln -s /opt/scripts/rabbitcasa/init.d/rabbitcasa /etc/init.d/
cp rabbitcasa.conf.example /etc/rabbitcasa.conf
chkconfig rabbitcasa on
service rabbitcasa start
```
