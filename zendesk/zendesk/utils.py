#!/usr/bin/env python
# -*- coding: utf-8 -*-
import frappe
import phonenumbers
from zendesk.zendesk.connector.zendesk_connector import ZendeskConnector
from frappe.data_migration.doctype.data_migration_connector.connectors.base import BaseConnection

def format_phone_number(doc, method):
	for item in doc.phone_nos:
		if item.phone:
			try:
				x = phonenumbers.parse(item.phone, "FR")
				item.phone = phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.E164)
			except Exception as e:
				frappe.throw(str(e))

def update_zendesk_phonenumbers():
	connector = ZendeskConnector(BaseConnection)
	users = connector.zenpy_client.users()

	for user in users:
		if user.phone is not None:
			try:
				old_phone = phonenumbers.parse(user.phone, "FR")
				new_phone = phonenumbers.format_number(old_phone, phonenumbers.PhoneNumberFormat.E164)

				if user.phone == new_phone:
					continue
				else:
					user.phone = new_phone

					try:
						response = connector.zenpy_client.users.update(user)
						print(response)
					except Exception as e:
						print(user.name)
						print(e)
			except phonenumbers.phonenumberutil.NumberParseException:
				continue

def merge_zendesk_users():
	connector = ZendeskConnector(BaseConnection)
	users = connector.zenpy_client.users()

	for user in users:
		if user.name.startswith("Caller +"):
			merge_user(user)

		elif user.name.startswith("+33") or user.name.startswith("+44"):
			merge_user(user)

def merge_user(user):
	connector = ZendeskConnector(BaseConnection)

	for existing_user in connector.zenpy_client.search(type='user', phone=user.phone):
		if existing_user.name != user.name:
			try:
				response = connector.zenpy_client.users.merge(source_user=user, dest_user=existing_user)
				print(response)
			except Exception as e:
				frappe.log_error(e, user.name)

	for existing_user in connector.zenpy_client.search(type='user', shared_phone_number=user.phone):
		if existing_user.name != user.name:
			try:
				response = connector.zenpy_client.users.merge(source_user=user, dest_user=existing_user)
				print(response)
			except Exception as e:
				frappe.log_error(e, user.name)

def update_all_contact_numbers():
	contacts = frappe.get_all("Contact")

	for contact in contacts:
		c = frappe.get_doc("Contact", contact.name)
		if c.phone:
			try:
				x = phonenumbers.parse(c.phone, "FR")
				c.phone = phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.E164)
			except Exception as e:
				print(c.name)
				print(str(e))

		if c.mobile_no:
			try:
				y = phonenumbers.parse(c.mobile_no, "FR")
				c.mobile_no = phonenumbers.format_number(y, phonenumbers.PhoneNumberFormat.E164)
			except Exception as e:
				print(c.name)
				print(str(e))

		if c.phone or c.mobile_no:
			try:
				c.save()
			except Exception as e:
				print(c.name)
				print(e)