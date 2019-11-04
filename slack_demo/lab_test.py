from pprint import pprint
import requests
import os
import slack
import json
import time
import netmiko
from common_functions import *
token = "xoxp-Fake_Token"      # found at 
# https://api.slack.com/web#authentication
username= 'username'
password= 'password'

#Fake channel
channel ="DPR9WUTEM"

#Post new message to slack channel in question
def post_to_slack(message, channel, token):
	slack_token = token
	client = slack.WebClient(token=slack_token)
	client.chat_postMessage(
	channel=channel,
	text=message)

#Pull last 1 message from slack channel in question
def get_last_message(token, channel):
	url= 'https://slack.com/api/conversations.history?token={}&channel={}&limit=1&pretty=1'.format(token, channel)
	r=requests.get(url)
	all_respoce = r.json()
	last_message = all_respoce['messages'][0]['text']
	return last_message

		  
def check_lab():
	lab_devices=[
	'192.168.0.12',
	'192.168.0.13',
	'192.168.0.14',
	'192.168.0.104',
	#Thrown in so I get some errors
	'1.1.1.1'
	]
	
	for ip in lab_devices:
		info_output = "*checking {}*".format(ip)
		post_to_slack(info_output, channel, token)
		net_connect=make_connection(ip, username, password)
		if net_connect==None:
			issue = "      can't connect to {}".format(ip)
			post_to_slack(issue, channel, token)
			continue
		command = 'show ip eigrp nei'
		output = send_command(net_connect,command)
		for neighbor in lab_devices:
			if ip == neighbor:
				continue
			if neighbor not in output:
				issue = '      {} is not found in the active neighbors'.format(neighbor)
				post_to_slack(issue, channel, token)
		command = 'show interfaces'
		output = send_command(net_connect,command)
		output = output.split("\n")
		interfaces= find_child_text (output, 'GigabitEthernet')
		for interface in interfaces:
			for line in interface:
				if "collisions" in line:
					if '0 collisions' not in line:
						interface_name = interface[0].split(' ')[0]
						issue = '      {} has collisions on {}'.format (interface_name, ip)
						post_to_slack(issue, channel, token)
	
	post_to_slack("done", channel, token)
		
		



functions=['say hi', 'check lab']

def say_hi():
	post_to_slack("hi", channel, token)
	post_to_slack("done", channel, token)
	
while 1==1:
	last_message = get_last_message(token, channel)
	if last_message in  functions:
		post_to_slack("processing", channel, token)
	if last_message == 'say hi':
		say_hi()
	if last_message == 'check lab':
		post_to_slack("processing", channel, token)
		check_lab()
	time.sleep(1)
