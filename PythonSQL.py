import mysql.connector
import os

class PythonToSQL:
    mydb = None
    def __init__(this):
        this.connect()

    def connect(this):
        #Makes it possible to run the same program off the Raspberry Pi and XAMPP
        if(os.name == 'posix'): #Pi
            SQL_datab = 'testchamber'
            SQL_ip = 'localhost'
            SQL_pn = '3306'
            SQL_usn = "admin"
            SQL_pwd = 'password'
        else: 
            SQL_datab = 'testchamber'
            SQL_ip = '127.0.0.1'
            SQL_pn = '3306'
            SQL_usn = "admin"
            SQL_pwd = 'password'

        #Connects to the MariaDB
        this.mydb = mysql.connector.connect(
            host=SQL_ip,
            port=SQL_pn,
            user=SQL_usn,
            password=SQL_pwd,
            database=SQL_datab
        )
        print('Connection data: '
                +'\n\t OS: '+os.name
                +'\n\t DB:'+SQL_datab
                +'\n\t IP:'+SQL_ip
                +'\n\t port:'+SQL_pn
                +'\n\t Username:'+SQL_usn
                +'\n\t pwd:'+SQL_pwd
                )


    def getTableContent(this,TABLENAME):
        #Reconnects to the db in case it has disconnected
        this.mydb.reconnect()
        """This function gathers the content from "TABLENAME", and outputs it into a touple-array.
        """
        cursor = this.mydb.cursor()
        print("Printing table!")

        #Select everything from the table
        cursor.execute('SELECT * FROM '+TABLENAME)

        #Creates touple array called data
        data = cursor.fetchall()

        return data

    def logImage(this,TABLENAME, FILENAME):
        #Reconnects to the db in case it has disconnected
        this.mydb.reconnect()
        ##
        #Is this better???
        print("Connected succesfully")
        cursor = this.mydb.cursor()
        this.createImageTable(TABLENAME)
        splitFileName = str(FILENAME).split("/")
        splitSplitFileName = str(splitFileName[1]).split(".")
        print("Filename:'"+str(splitSplitFileName[0])+"'")

        print('INSERT INTO '+TABLENAME
            + ' (ts, filename) '
            + 'VALUES ('
            + 'CURRENT_TIMESTAMP, "'
            #+ str(splitSplitFileName[0])
            + str(FILENAME)
            + '")')

        cursor.execute(
            'INSERT INTO '+TABLENAME
            + ' (ts, filename) '
            + 'VALUES ('
            + 'CURRENT_TIMESTAMP, "'
            #+ str(splitSplitFileName[0])
            + str(FILENAME)
            + '")')

        print("Executed!")

        this.mydb.commit()


    def dropTable(this,TABLENAME):
        #Reconnects to the db in case it has disconnected
        this.mydb.reconnect()
        """This function allows 
        """
        cursor = this.mydb.cursor()

        cursor.execute('DROP TABLE '+TABLENAME)

        print("Table "+TABLENAME+" has been deleted!")
        this.mydb.commit()


    def postData(this,TABLENAME,COLUMNS, DATA):
        #Reconnects to the db in case it has disconnected
        this.mydb.reconnect()
        cursor = this.mydb.cursor()
        
        datastring =''
        columnsstring = 'ts'
        print("Strings prepared")

        for i in range(0,len(DATA)):
            datastring = datastring + ', ' + str(DATA[i])
            columnsstring = columnsstring +', '+str(COLUMNS[i+2])
        print("datastring: "+datastring)
        print("columnsstring: "+columnsstring)

        sql = (
            'INSERT INTO '+TABLENAME
            + '('
            + columnsstring
            +')'
            +'VALUES('
            + 'CURRENT_TIMESTAMP'
            + datastring
            + ')')

        print(sql)

        cursor.execute(sql)

        this.mydb.commit()

    """!
    def createTable(this,TABLENAME):
        #Reconnects to the db in case it has disconnected
        this.mydb.reconnect()
        print("Connected succesfully")
        cursor = this.mydb.cursor()

        sql = ("SHOW TABLES")

        cursor.execute(sql)

        error = 0

        for element in cursor:
            print(element[0])
            if(element[0] == TABLENAME):
                error = -1
        
        #Laver en string for det nye table
        datastring = ''
        for m in range(1,5):
            for s in range(1,5):
                datastring = datastring + ", Modul"+str(m)+"sensor"+str(s)+" VARCHAR(30)"

        if error == 0:
            sql = ("CREATE TABLE "
                    + TABLENAME
                    + " (id INT AUTO_INCREMENT PRIMARY KEY, "
                    + "ts TIMESTAMP, "
                    +datastring
                    + ")")

            cursor.execute(sql)

            print("Table "+TABLENAME+" has been created!")
        else:
            print("Error: Table hasn't been created")

        this.mydb.commit()

        return error
        """

    def getTableNames(this):
        #Reconnects to the db in case it has disconnected
        this.mydb.reconnect()

        print("Getting tables!")
        cursor = this.mydb.cursor()

        sql = ("SHOW TABLES")

        cursor.execute(sql)

        result = cursor.fetchall()

        tablenames = [x[0] for x in result]

        return tablenames

    def getColoums(this,TABLENAME):
        #Reconnects to the db in case it has disconnected
        this.mydb.reconnect()
        cursor = this.mydb.cursor()

        sql = ("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"
                +str(TABLENAME)
                +"' ORDER BY ORDINAL_POSITION")

        print(sql)

        cursor.execute(sql)

        result = cursor.fetchall()
        
        column = [x[0] for x in result]

        return column

    def createtesttable(this,tableelements):
        #Reconnects to the db in case it has disconnected
        this.mydb.reconnect()
        print("Entered Createtesttable")
        cursor = this.mydb.cursor()

        sql = ("SHOW TABLES")

        cursor.execute(sql)

        error = 0

        Chigh = 0

        print("Exsisting tables:")
        for element in cursor:
            print("\t"+str(element[0]))
            if str(element[0]).startswith('test'):
                dbstring = str(element[0]).split('_')
                print("[0]"+str(dbstring[0])+", [1]: "+str(dbstring[1]+", [1] in int:"+str(int(dbstring[1]))))
                if int(dbstring[1]) > Chigh:
                    Chigh = int(dbstring[1])
        
        print("Latest table: test_"+str(Chigh))
        
        TABLENAME = 'test_'+str(Chigh+1)

        print("Next table: "+TABLENAME)

        datastring =''

        for i in range(0,len(tableelements)):
            datastring = datastring + ', ' + str.lower(tableelements[i]) +" VARCHAR(30) NOT NULL"
        
        print(datastring)

        if error == 0:
            sql = ("CREATE TABLE "
                    + TABLENAME
                    + " (id INT AUTO_INCREMENT PRIMARY KEY, "
                    + "ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
                    + datastring
                    + ")")

            print(sql)

            cursor.execute(sql)

            print("Table "+TABLENAME+" has been created!")
        else:
            print("Error: Table hasn't been created")

        this.mydb.commit()

        return error

    def createImageTable(this,TABLENAME):
        #Reconnects to the db in case it has disconnected
        this.mydb.reconnect()
        print("Connected succesfully")
        cursor = this.mydb.cursor()

        sql = ("SHOW TABLES")

        cursor.execute(sql)

        error = 0

        for element in cursor:
            print(element[0])
            if(element[0] == TABLENAME):
                error = -1
        
        if error == 0:
            sql = ("CREATE TABLE "
                    + TABLENAME
                    + " (id INT AUTO_INCREMENT PRIMARY KEY, "
                    + "ts TIMESTAMP, "
                    + "filename VARCHAR(30)"
                    + ")")

            cursor.execute(sql)

            print("Table "+TABLENAME+" has been created!")
        else:
            print("Error: Table hasn't been created")

        this.mydb.commit()

        return error