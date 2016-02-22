test -f /etc/httpd/conf.d/fred-rdap-apache.conf || ln -s /usr/share/fred-rdap/apache.conf /etc/httpd/conf.d/fred-rdap-apache.conf
test -f /var/log/fred-rdap.log || touch /var/log/fred-rdap.log; chown apache.apache /var/log/fred-rdap.log; chcon -t httpd_log_t /var/log/fred-rdap.log
