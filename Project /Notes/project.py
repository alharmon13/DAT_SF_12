{u'labels': [], u'updated_at': u'2014-06-12T23:16:54Z', u'locked_until': None, u'received_at': u'2014-06-02T23:06:06Z', u'active_attachments_count': 0, u'id': 111080, u'custom_fields': {u'dm': None, u'emailformdropdown': u'-please make a selection-', u'big_team': None, u'mobile': None, u'form_source': None, u'ticket_groups': None, u'priority_support': False, u'fb_pm': None}, u'subject': u'Fresh from the Frog - News from JFDI.Asia', u'changed_at': u'2014-06-12T23:16:54Z', u'priority': 4, u'opened_at': u'2014-06-02T23:09:50Z', u'active_at': u'2014-06-02T23:09:50Z', u'_links': {u'customer': {u'href': u'/api/v2/customers/88959359', u'class': u'customer'}, u'locked_by': None, u'attachments': {u'count': 0, u'href': u'/api/v2/cases/111080/attachments', u'class': u'attachment'}, u'self': {u'href': u'/api/v2/cases/111080', u'class': u'case'}, u'labels': {u'href': u'/api/v2/cases/111080/labels', u'class': u'label'}, u'feedbacks': None, u'case_links': {u'href': u'/api/v2/cases/111080/links', u'class': u'case_link'}, u'notes': {u'count': 0, u'href': u'/api/v2/cases/111080/notes', u'class': u'note'}, u'draft': {u'href': u'/api/v2/cases/111080/replies/draft', u'class': u'reply'}, u'replies': {u'count': 1, u'href': u'/api/v2/cases/111080/replies', u'class': u'reply'}, u'macro_preview': {u'href': u'/api/v2/cases/111080/macros/preview', u'class': u'macro_preview'}, u'message': {u'href': u'/api/v2/cases/111080/message', u'class': u'email'}, u'assigned_user': {u'href': u'/api/v2/users/10024442', u'class': u'user'}, u'assigned_group': {u'href': u'/api/v2/groups/19411', u'class': u'group'}, u'history': {u'href': u'/api/v2/cases/111080/history', u'class': u'history'}}, u'type': u'email', u'blurb': u"We're launching JFDI Discovery and opening applications to our 2014B Accelerator program!\n------------------------------------------------------------\nhttp://us4.campaign-archive1.com/?u=3ba2714ad84b1bc86a1b98daf&id=c540984bd2&e=56c1858992\n\n\n** JFDI ", u'status': u'closed', u'first_resolved_at': u'2014-06-02T23:09:54Z', u'description': u'', u'label_ids': [], u'active_notes_count': 0, u'resolved_at': u'2014-06-02T23:09:54Z', u'language': None, u'created_at': u'2014-06-02T23:06:06Z', u'external_id': None, u'first_opened_at': u'2014-06-02T23:09:50Z'}



u'received_at'
u'id'
u'ticket_groups'
u'priority_support'
u'opened_at'
u'replies'
u'assigned_group'
u'type': u'email'
u'status'
u'first_resolved_at'
u'resolved_at'
u'created_at'
u'first_opened_at'


List of dictionaries (json)
Create a list of desired keys from dictionary
result = {}
for i in range(len(listDictionaries)):
	for key in listOfKeys:
		result[key] = listDictionaries[i][key]

Then use this: http://stackoverflow.com/questions/18837262/convert-python-dict-into-a-dataframe
