#!C:/Users/rdybs/AppData/Local/Programs/Python/Python310 python3

##
# @mainpage HTTP request handler for plant test chamber
#
# @section description_main Description
#  
# testChamberServer is a package developed to act as a link beteween a microcontroller,
# a user and a database.
#
# The package consists of three modules.
# - The main.py, handling the http request server
# - The PythonSQL.py, handling communication to the MariaDB database of the project
# - RQST.py, pushes data towards an ESP, as if it were an client.
#
#
# The project is created for AAU EIT2 group B211 as part of the P2 project.
# Project created 14/4-2022
# Updated 02/5-2022
#
# @section notes_main Notes
# - This project is meant to be used with groupt B211' programmed ESP-01, and ESP32-CAM
# - It is meant to be run on a Raspberry Pi
# - This is a work under development, and is not meant for widespread usage
#
# @remark Bonjour
#
#
# @bug Program stops working after visiting delete_table

import sys

sys.path.append('/var/www/html')
import cgi
from datetime import datetime
from genericpath import exists
from http import server
from urllib import response
import mysql.connector
from http.server import BaseHTTPRequestHandler, HTTPServer
import PythonSQL
import os
import RQST


# Allows the same code to be run on both raspberry pi and the development laptop
if(os.name == 'posix'):
    hostName = ""
    serverPort = 8080
else:
    hostName = "localhost"
    serverPort = 8000


class testChamberServer(BaseHTTPRequestHandler):
    """Documentation of testChamberServer
    This is the main class running the program, based on the \package http.server.

    @param What happens when you do param

    @func Function?
    """
    ##
    # resond is respond 100
    #

    def respond(self, response=200):
        """        
        Respond is a short function, as to create a response to the request
        By default, it will respond with a 200, meaning "OK".
        If it senses a request for a .html document, it wil open that file and respond with the lines.

        @param response
        @notes The function only responds in content-type: text/html at the minute. This might be changed in a future version.
        """
        try:
            if self.path.endswith(".html"):
                if os.path.exists(os.curdir+os.sep+self.path) == False:
                    self.path = '/'
                    raise Exception("File doesn't exists")
        except Exception as error:
            print(str(error))
            response = 500

        self.send_response(response)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.flush_headers()
        # Prints a .html document as a response
        if self.path.endswith(".html"):
            file = open(os.curdir+os.sep+self.path)
            self.wfile.write(bytes(file.read(), "utf-8"))
            file.close()
            self.wfile.flush()

    def redirect(self, destination):
        url = 'http://'+self.address_string() + ':' + str(serverPort)+destination
        print("Redirecting to: "+url)
        self.send_response(301)
        self.send_header('Location', url)
        self.end_headers()
        self.flush_headers()

    def do_HEAD(self):
        """! do_HEAD reponds to HEAD request with a simple header.
        """
        self.respond(200)

    # Handles DELETE requests - currently only able to truncate table "measureddata"
    def do_DELETE(self):
        """do_DELETE handles DELETE requests to the server. It is requested through the path /delete/?tablename, 
        and allows to delete a table
        @param tablename
        """
        print("DELETE TIME!")
        # Checks path
        if self.path.startswith('/delete'):
            self.deleteTable()
        else:
            self.respond(404)

    # Handles postrequests - responds with an error if it is an invalid target

    def do_POST(self):
        if self.path.startswith('/post'):
            print("Looking for path "+str(self.path))
            self.uploadData()
        elif self.path == '/createtable':
            self.createTable()
        elif self.path == '/delete':
            self.do_DELETE()
        elif self.path == '/update':
            self.update()
        else:
            self.respond(404)
            self.wfile.write("Post request denied for {}".format(
                self.path).encode('utf-8'))

    def do_GET(self):
        ##
        #Is this how u document better? IDK
        
        # Redirects /pictest to /picturetest.html
        print("Looking for path "+str(self.path))
        

        #Dette er ikke nødvendigt for koden, men er en spændende måde at afkode requesten, uden at få brug for CGI form metoden.
        length = self.headers.get('Content-Length')
        print("Content-length is "+str(length))
        if length != None:
            field_data = self.rfile.read(int(length))
            string = field_data.decode("utf-8")
            print("Decoded content: "+string)
            content = string.split("&")

            keylist = []
            valuelist = []

            for element in content:
                keylist.append(element.split("=")[0])
                valuelist.append(element.split("=")[1])
            
            for i in range(0, len(keylist)):
                print("Element["+str(i)+"] - Key: "+str(keylist[i]+", value: "+str(valuelist[i])))
        #Junk slut

        if self.path == '/pictest':
            self.redirect('/picturetest.html')
        elif self.path == '/update':
            self.redirect('/inputform.html')
        # Creates a new table with all values
        elif self.path.startswith('/createtable/?'):
            self.createTable()
        elif self.path.startswith('/printtable'):
            self.printTable()
        elif self.path == '/delete':
            self.redirect('/deletepage_laptop.html')
        elif self.path == '/':
            self.tableoverview()
        elif self.path.endswith('.html'):
            self.respond()
        elif self.path.endswith('.png'):
            print("\t RETURNING PICTUIRE IS NOT POSSIBLE ATM!")
            self.respond(501)
        else:
            self.respond(404)
            self.wfile.write("Request for {} denied. ".format(
                self.path).encode('utf-8'))
            self.wfile.write("Site does not exist.".encode('utf-8'))

    def printTable(self):
        self.respond(200)

        if self.path == '/printtable':
            tablename = 'measureddata'
            print("no table found")
        else:
            table = self.path.split("?")
            tablename = table[1]
            print("Table found: "+tablename)

        self.setupHTML()

        # Sets up HTML table
        self.wfile.write(bytes('<h1> Table "'+str(tablename) +
                         '" contents: <table> <tr>', "utf-8"))
        print("Started setup")

        # Prints column names
        columnNames = mydb.getColoums(tablename)
        tableContent = mydb.getTableContent(TABLENAME=str(tablename))
        print("Found content")

        for column in columnNames:
            self.wfile.write(bytes("<th>"+str(column)+": </th>", "utf-8"))
        self.wfile.write(bytes("</tr>", "utf-8"))

        for element in tableContent:
            self.wfile.write(bytes("<tr>", "utf-8"))
            for i in range(0, len(element)):
                self.wfile.write(
                    bytes("<td>"+str(element[i])+"</td>", "utf-8"))
            self.wfile.write(bytes("</tr>", "utf-8"))
        self.wfile.write(bytes("</table></body></html>", "utf-8"))

    def tableoverview(self):
        self.respond(200)
        self.setupHTML()
        self.wfile.write(("<h2> Pick a table </h2>").encode())

        data = mydb.getTableNames()

        for element in data:
            self.wfile.write(bytes('<button type="button" id="'+str(element) +
                             '">View table of '+str(element)+'</button><br>', "utf-8"))

        self.wfile.write(bytes(
            '<br><br><br><button type="button" id="deletepage"> Go to the delete page </button><br>', "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        self.wfile.write(bytes('<script type="text/javascript">', "utf-8"))

        for element in data:
            self.wfile.write(bytes(' document.getElementById("' +
                             str(element)+'").onclick = function() {\n', "utf-8"))
            self.wfile.write(bytes('    location.href = "http://localhost:' +
                             str(serverPort)+'/printtable/?'+str(element)+'";\n', "utf-8"))
            self.wfile.write(bytes(' };\n', "utf-8"))

        self.wfile.write(bytes(
            ' document.getElementById("deletepage").onclick = function() {\n', "utf-8"))
        self.wfile.write(bytes(
            '    location.href = "http://localhost:'+str(serverPort)+'/delete";\n', "utf-8"))
        self.wfile.write(bytes(' };\n', "utf-8"))
        self.wfile.write(bytes('</script>', "utf-8"))

    def uploadData(self):
        print("Inside uploadData!")
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'},  # Only accepts POST
        )

        # Checks for valid api_key & path
        try:
            if form.getvalue("api_key") != 'ABC123000':
                raise Exception("Invalid API-key")
            if self.path == '/postimg':
                self.imgcase(form)
            elif self.path == '/postdata':
                self.uploadToDb(form)
            else:
                raise Exception("Wrong path!")
        except Exception as error:
            self.respond(401)
            self.wfile.write(bytes("POST denied: "+str(error)+"! ", "utf-8"))
            print("Error: "+str(error))

    def uploadToDb(self, form):
        datalist = []
        tablename = form.getvalue('tablename')
        columnList = mydb.getColoums(tablename)
        key = form.keys()
        for column in columnList:
            for keys in key:
                if str(keys).lower() == column:
                    datalist.append(form.getvalue(str(keys)))

        # Prints the data recieved from the keys
        print("datalist:")
        for i in range(0, len(datalist)):
            print(datalist[i], end=' ')

        # Inserts the datalist into whatever the tablename is
        try:
            if (len(datalist)+2) != len(columnList):
                raise Exception("Invalid lenght")
            mydb.postData(TABLENAME=tablename,
                          DATA=datalist, COLUMNS=columnList)
            self.respond(200)
            self.wfile.write("POST request Accepted for {}".format(
                self.path).encode('utf-8'))
        except Exception as error:
            self.respond(406)
            self.wfile.write(("POST denied for {}. Exception: " +
                             str(error)).format(self.path).encode('utf-8'))

    def imgcase(self, form):
        """!Function running once /pictest is called.
        The purpose of this code is to upload a picture to the webserver,
        and log the path in the MariaDB database.

        Raises:
            Exception: If the filepath doesn't exsist,  

        Returns:
            _type_: _description_
        """
        print("Img recieved!")
        now = datetime.now()

        current_time = now.strftime("%d%m%Y_%H_%M_%S")

        filename = os.path.basename(current_time)
        filename = 'images/'+filename + ".png"
        # Don't overwrite files
        try:
            if os.path.exists(filename):
                raise Exception("Filename exists")

            self.saveToFile(filename, form)

            mydb.logImage(TABLENAME='imagelog', FILENAME=filename)
            self.respond(200)
            self.wfile.write(
                bytes("<html><head> Succes! </head><body>", "utf-8"))
            self.wfile.write(
                bytes('<br>Successfully posted file "' + filename+'" to server', "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
        except Exception as error:
            self.respond(409)
            reply_body = '"%s" already exists\n' % filename
            self.wfile.write(reply_body.encode('utf-8'))
        return self  # Nødvendig??

    def deleteTable(self):
        print("CORRECT STRING!")
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'DELETE'},
        )
        table = form.getvalue('tablename')
        password = form.getvalue('password')
        print("Tablename: "+str(table))
        print("Password: "+str(password))

        # Gets all tablenames from the database
        tablenames = mydb.getTableNames()
        print(str(tablenames))
        try:
            exists = table in tablenames
            if password != 'ABC123000':
                response = 401
                raise Exception("Invalid password")
            if exists == False:
                response = 404
                raise Exception("Table '"+table+"' doesn't exsist")
            print("Dropping table: "+table)
            mydb.dropTable(TABLENAME=table)
            self.respond(200)
            self.wfile.write(
                ("Table '"+table+"' deleted succesfully").encode())
        except Exception as error:
            self.respond(response)
            self.wfile.write(("DELETE denied: "+str(error)).encode())

    def createTable(self):
        print("/createtable recieved!")
        print(self.headers)
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'},
        )

        if form.getvalue("api_key") == 'ABC123000':
            print("Form set!")
            print(form)

            modulelist = []
            for element in form:
                if element.startswith('Module') & element.endswith('info'):
                    modulelist.append(form.getvalue(element))

            print("These are the new elements!")
            for element in modulelist:
                print(str(element))

            datalist = []

            for element in modulelist:
                sensorlist = str(element).split(':')
                for i in range(0, len(sensorlist)):
                    datalist.append(sensorlist[i])

            print("datalist:")
            for i in range(0, len(datalist)):
                print(datalist[i])

            mydb.createtesttable(tableelements=datalist)
            self.respond(200)
            self.wfile.write("POST request Accepted for {}".format(
                self.path).encode('utf-8'))

        else:
            self.respond(401)
            self.wfile.write(bytes("POST denied: Invalid API-key", "utf-8"))

        for x in form:
            self.wfile.write(bytes("<br>Type " + str(x) +
                             " contains value " + str(form.getvalue(x)), "utf-8"))

    def update(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'},
        )

        keys = form.keys()
        content = {}
        for key in keys:
            if(key != 'submit'):
                content.update({key:form.getvalue(key)})

        print(str(content))
        
        self.respond(200)
        
        response = RQST.starttest(content)

        self.wfile.write(bytes(response))


    def setupHTML(self):
        file = open(os.curdir+os.sep+'setuphtml.html')
        filecontent = file.read()
        file.close()
        self.wfile.write(bytes(filecontent, "utf-8"))
        self.wfile.flush()

    def saveToFile(self, filename, form):
        filebuffer = form.getvalue("imageFile")
        f = open(filename, 'wb')
        f.write(bytearray(filebuffer))
        f.close()


if __name__ == "__main__":
    # Starter serveren op på hostname, serverport, og benytter handleren "testChamberServer"

    webServer = HTTPServer((hostName, serverPort), testChamberServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        mydb = PythonSQL.PythonToSQL()
        webServer.serve_forever()
    except mysql.connector.errors.InterfaceError:
        print("Error: MySQL not running!")
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
