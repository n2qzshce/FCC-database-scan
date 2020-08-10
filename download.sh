#!/bin/bash
 
# Hamdb
# Copyright (C) 2001-2008 Anthony Good
 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 
# You may contact the author at goody@fast.net
 
# 07/31/2008 - Modified to download/import daily transaction files - AE5IR
 
STOREDIR=.
VERSION=0.7.0
CONFIGFILE=./hamdb.cnf
DEBUG=1
WGET=/usr/bin/wget
UNZIP=/usr/bin/unzip
DAY=`date -d "-1 day" | tr '[:upper:]' '[:lower:]' | sed 's/\([a-z]*\).*/\1/'`
DAY=sun
if [ ${DAY} == sun ]; then
    #FCC_FILE_LOCATION=http://wireless.fcc.gov/uls/data/complete/l_amat.zip
    FCC_FILE_LOCATION=ftp://wirelessftp.fcc.gov/pub/uls/complete/l_amat.zip
    DOWNLOAD_FILE=l_amat.zip
else
    #FCC_FILE_LOCATION=http://wireless.fcc.gov/uls/data/daily/l_am_${DAY}.zip
    FCC_FILE_LOCATION=ftp://wirelessftp.fcc.gov/pub/uls/daily/l_ac_${DAY}.zip
    DOWNLOAD_FILE=l_ac_${DAY}.zip
fi
if [ ${DEBUG} -eq 1 ]; then
  echo "In debug mode..."
fi
 
if [ -f ${CONFIGFILE} ]; then
  . ${CONFIGFILE}
else
  echo -n "Hamdb configuration file ${CONFIGFILE} not found.  Would you like to create the file? [y/N]"
  read userinput
  #echo -n "Enter MySQL login with God-like privleges: "
  #read MYSQLGODUSERNAME
  #echo -n "Enter MySQL God password: "
  #read MYSQLGODPASSWD
  #echo -n "Enter new MySQL user to create for hamdb database access: "
  echo -n "Enter MySQL username: "
  read MYSQLUSERNAME
  #echo -n "Enter new MySQL user's password: "
  echo -n "Enter MySQL user's password: "
  read MYSQLPASSWD
  #echo "show databases;" | mysql --user=${MYSQLGODUSERNAME} --password=${MYSQLGODPASSWD}
  echo "#!/bin/sh" > ${CONFIGFILE}
  echo "MYSQLUSERNAME=$MYSQLUSERNAME" >> ${CONFIGFILE}
  echo "MYSQLPASSWD=$MYSQLPASSWD" >> ${CONFIGFILE}
  chmod 700 ${CONFIGFILE}
fi
 
if [ ${DEBUG} -eq 1 ]; then
  echo "Username is ${MYSQLUSERNAME}"
  echo "Password is ${MYSQLPASSWD}"
  echo "\s" | mysql --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}|grep "Server version:" | awk '{print $3}'
fi
 
case "$1" in
 
  getfccfile)
      echo "Downloading database from FCC..."
      #$WGET -nd --passive-ftp -d ftp://ftp.fcc.gov/pub/Bureaus/Wireless/Databases/uls/complete/l_amat.zip
      $WGET -nd -d $FCC_FILE_LOCATION
  ;;
 
  populatedb)
    if [ ! -d ${STOREDIR} ]; then
      mkdir ${STOREDIR}
    fi
    cd ${STOREDIR}
 
    if [ ! -f "${DOWNLOAD_FILE}" ]; then
      echo "Downloading database from FCC..."
      #wget -nd --passive-ftp -d ftp://ftp.fcc.gov/pub/Bureaus/Wireless/Databases/uls/complete/l_amat.zip
      $WGET -nd -d $FCC_FILE_LOCATION
 
    fi
 
    if [ ! -f EN.dat ]; then
      echo "Unzipping database file EN.dat..."
      ${UNZIP} ./${DOWNLOAD_FILE} EN.dat
    fi
 
    if [ ! -f AM.dat ]; then
      echo "Unzipping database file AM.dat..."
      ${UNZIP} ./${DOWNLOAD_FILE} AM.dat
    fi
 
    if [ ! -f HD.dat ]; then
      echo "Unzipping database file HD.dat..."
      ${UNZIP} ./${DOWNLOAD_FILE} HD.dat
    fi
 
    if [ ! -f tempfile_en.txt ]; then
      echo "Creating temporary file for table en..."
      cat ./EN.dat |sed s/[\\\"]//g|awk -F "|" '{print "\""$2"\",\""$5"\",\""$8"\",\""$9"\",\""$10"\",\""$11"\",\""$16"\",\""$17"\",\""$18"\",\""$19"\""}'>./tempfile_en.txt
    fi
 
    if [ ! -f tempfile_am.txt ]; then
      echo "Creating temporary file for table am..."
      cat ./AM.dat |sed s/[\\\"]//g|awk -F "|" '{print "\""$2"\",\""$5"\",\""$6"\",\""$7"\",\""$8"\",\""$10"\",\""$16"\",\""$17"\""}'>./tempfile_am.txt
    fi
 
    if [ ! -f tempfile_hd.txt ]; then
      echo "Creating temporary file for table hd..."
      cat ./HD.dat |sed s/[\\\"]//g|awk -F "|" '{print "\""$2"\",\""$5"\",\""$6"\",\""$8"\",\""$9"\""}'>./tempfile_hd.txt
    fi
 
    if [ ${DAY} == sun ]; then
 
    echo "Creating temporary tables in Mysql..."
 
    echo "use fcc_amateur;drop table if exists en_temp;create table en_temp (fccid int not null, callsign varchar(8) not null, primary key(fccid),full_name varchar(128),first varchar(20),middle varchar(1), last varchar(20), address1 varchar(64), city varchar(20), state varchar(2), zip varchar(10), index idx_zip (zip), index idx_callsign (callsign));"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
 
    #echo "use fcc_amateur;drop table if exists en_temp;create table en_temp (fccid int, callsign varchar(8) not null, primary key(callsign),full_name varchar(128),first varchar(20),middle varchar(1), last varchar(20), address1 varchar(64), city varchar(20), state varchar(2), zip varchar(10), index idx_zip (zip), index idx_fccid (fccid));"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=$MYSQLPASSWD
 
    echo "use fcc_amateur;drop table if exists am_temp;create table am_temp (fccid int not null, callsign varchar(8) not null, primary key(fccid), class varchar(1), col4 varchar(1), col5 varchar(2), col6 varchar(3), former_call varchar(8), former_class varchar(1), index idx_callsign (callsign), index idx_class(class));"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
 
    #echo "use fcc_amateur;drop table if exists am_temp;create table am_temp (fccid int, callsign varchar(8) not null, primary key(callsign), class varchar(1), col4 varchar(1), col5 varchar(2), col6 varchar(3), former_call varchar(8), former_class varchar(1), index idx_fccid (fccid), index idx_class(class));"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
 
    echo "use fcc_amateur;drop table if exists hd_temp;create table hd_temp (fccid int not null, callsign varchar(8) not null, primary key(fccid), status varchar(1), index idx_callsign (callsign), index idx_status (status), grant_date date, expire_date date);"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
 
    echo "Populating database table en..."
 
    echo "use fcc_amateur;load data local infile '${STOREDIR}/tempfile_en.txt' replace into table en_temp fields terminated by ',' enclosed by '\"' lines terminated by '\n';"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD} --local-infile=1
 
    echo "use fcc_amateur;rename table en to en_old, en_temp to en;drop table en_old;"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
 
    echo "Populating database table am..."
 
    echo "use fcc_amateur;load data local infile '${STOREDIR}/tempfile_am.txt' replace into table am_temp fields terminated by ',' enclosed by '\"' lines terminated by '\n';"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD} --local-infile=1
 
    echo "use fcc_amateur;rename table am to am_old, am_temp to am;drop table am_old;"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
 
    echo "Populating database table hd..."
 
    echo "use fcc_amateur;load data local infile '${STOREDIR}/tempfile_hd.txt' replace into table hd_temp fields terminated by ',' enclosed by '\"' lines terminated by '\n' (fccid, callsign,status,@grant_date, @expire_date) set grant_date=str_to_date(@grant_date, '%m/%d/%Y'), expire_date=str_to_date(@expire_date, '%m/%d/%Y');"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD} --local-infile=1
 
    echo "use fcc_amateur;rename table hd to hd_old, hd_temp to hd;drop table hd_old;"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
 
    else
 
    echo "Updating database table en..."
 
    echo "use fcc_amateur;load data local infile '${STOREDIR}/tempfile_en.txt' replace into table en fields terminated by ',' enclosed by '\"' lines terminated by '\n';"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD} --local-infile=1
 
    echo "Updating database table am..."
 
    echo "use fcc_amateur;load data local infile '${STOREDIR}/tempfile_am.txt' replace into table am fields terminated by ',' enclosed by '\"' lines terminated by '\n';"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD} --local-infile=1
 
    echo "Updating database table hd..."
 
    echo "use fcc_amateur;load data local infile '${STOREDIR}/tempfile_hd.txt' replace into table hd fields terminated by ',' enclosed by '\"' lines terminated by '\n' (fccid, callsign,status,@grant_date, @expire_date) set grant_date=str_to_date(@grant_date, '%m/%d/%Y'), expire_date=str_to_date(@expire_date, '%m/%d/%Y');"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD} --local-infile=1
 
    fi
 
    if [ ${DEBUG} -eq 0 ]; then
      echo "Cleaning up..."
      rm ./tempfile_*.txt
      rm ./*.dat
      rm ./*.zip
#      rm ./counts
      cd -
#      rmdir ${STOREDIR}
    fi
 
    echo "Done..."
 
    ;;
 
  makedatabase)
 
    echo "Creating database fcc_amateur...";
 
    echo "create database fcc_amateur;"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
 
    echo "use fcc_amateur;create table en (fccid int not null, callsign varchar(8) not null, primary key(fccid),full_name varchar(128),first varchar(20),middle varchar(1), last varchar(20), address1 varchar(64), city varchar(20), state varchar(2), zip varchar(10), index idx_zip (zip), index idx_callsign (callsign));"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
 
    echo "use fcc_amateur;create table am (fccid int not null, callsign varchar(8) not null, primary key(fccid), class varchar(1), col4 varchar(1), col5 varchar(2), col6 varchar(3), former_call varchar(8), former_class varchar(1), index idx_callsign (callsign), index idx_class(class));"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
 
    echo "use fcc_amateur;create table hd (fccid int not null, callsign varchar(8) not null, primary key(fccid), status varchar(1), index idx_callsign (callsign), index idx_status (status), grant_date date, expire_date date);"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
 
  ;;
 
  removedatabase)
    echo "drop database fcc_amateur;"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
  ;;
 
  removetables)
    echo "use fcc_amateur;drop table if exists en;drop table if exists am;drop table if exists hd;drop table if exists en_temp;drop table if exists am_temp;drop table if exists hd_temp"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
  ;;
 
  zipcodebatch)
    echo "use fcc_amateur;select en.callsign,class,first,last,address1,city,state,zip from en, am, hd  where en.fccid=am.fccid and en.fccid=hd.fccid and hd.status=\"A\" and zip like \"$2%\";" | mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD} -N --batch | awk -F "\t" '{print $1","$2","$3","$4","$5","$6","$7","$8}'
  ;;
 
  dumptableen)
    echo "use fcc_amateur;select * from en;"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
  ;;
 
  dbcount)
    echo "Table en count: "
    echo "use fcc_amateur;select COUNT(fccid) from en;"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
    echo "Table am count: "
    echo "use fcc_amateur;select COUNT(fccid) from am;"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
    echo "Table hd count: "
    echo "use fcc_amateur;select COUNT(fccid) from hd;"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
    echo "Table hd status counts: "
    echo "use fcc_amateur;select status, count(fccid) from hd group by status;"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
  ;;
 
  -h | --help | help)
    echo "Help:"
    ;;
 
  -v | --version | version)
    echo ${VERSION}
    ;;
 
  like)
    CALLSIGN=`echo $2|sed y/abcdefghijklmnopqrstuvwxyz/ABCDEFGHIJKLMNOPQRSTUVWXYZ/`
    echo "use fcc_amateur;select en.callsign, am.class, full_name, address1, city, state, zip, former_call from en, am, hd where en.fccid=am.fccid and en.fccid=hd.fccid and hd.status=\"A\" and en.callsign like  \"$CALLSIGN%\";"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
  ;;
 
  *)
    CALLSIGN=`echo $1|sed y/abcdefghijklmnopqrstuvwxyz/ABCDEFGHIJKLMNOPQRSTUVWXYZ/`
    echo "use fcc_amateur;select en.callsign, am.class, full_name, address1, city, state, zip, former_call from en, am, hd where en.fccid=am.fccid and en.fccid=hd.fccid and hd.status=\"A\" and en.callsign=\"$CALLSIGN\";"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
    #echo "use fcc_amateur;select * from en where en.callsign=\"$CALLSIGN\";"|mysql -h 127.0.0.1 --user=${MYSQLUSERNAME} --password=${MYSQLPASSWD}
    exit 0
esac
