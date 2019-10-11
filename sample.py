from flask import Flask, jsonify
import saboo
app = Flask(__name__)
#app.config['odoo_conf'] = saboo.client._parse_config(['odoo-import.bin', '-c', 'import.conf'])

@app.route('/')
def hello_world():
   return jsonify({"message": "Hello World!"})

@app.route('/getlead', methods=['GET'])
def getCrmLead():
    name = 'crm.lead'
    print("1----------------------",name)
    client = saboo.client
    print("2----------------------",client)
    client.conf = client._parse_config(['odoo-import.bin', '-c', 'import.conf'])
    print("3----------------------",client.conf)
    client._init_odoo(client.conf)
    odoo = saboo.tools.login(client.conf)
    print("4----------------------",odoo)
    crmLeads = odoo.env[name]
    ids = crmLeads.search([], limit =100)
    response = {}
    for id in ids:
	    lead = crmLeads.browse(id)
	   # print(lead.name)
	   # print(lead.partner_name)
	    response[id] = {"name":lead.name,"customer":lead.partner_name}
    return response

if __name__ == '__main__':
	app.run()