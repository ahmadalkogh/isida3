#!/usr/bin/python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------- #
#                                                                             #
#    Plugin for iSida Jabber Bot                                              #
#    Copyright (C) 2012 diSabler <dsy@dsy.name>                               #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                             #
# --------------------------------------------------------------------------- #

AGE_DEFAULT_LIMIT = 10
AGE_MAX_LIMIT = 100

def true_age_stat(type, jid, nick, text):
	text = text.strip()
	if text and text.isdigit(): llim = int(text)
	else:
		try: llim = GT('age_default_limit')
		except: llim = AGE_DEFAULT_LIMIT
	if llim not in range(1,AGE_MAX_LIMIT): llim = AGE_DEFAULT_LIMIT
	t_age_tmp = cur_execute_fetchmany('select jid,sum(age+(status = 0)::boolean::int*(%s-time)) as sum_age from age where room=%s group by jid order by sum_age desc;',(int(time.time()),jid),llim)
	t_age = []
	for t in t_age_tmp:
		tmp = cur_execute_fetchone('select nick from age where room=%s and jid=%s order by status,-time',(jid,t[0]))
		t_age.append((tmp[0],t[1]))
	msg = L('Age statistic:\n%s','%s/%s'%(jid,nick)) % '\n'.join(['%s\t%s' % (t[0],un_unix(t[1])) for t in t_age])
	send_msg(type, jid, nick, msg)

def true_age_split(type, jid, nick, text):
	true_age_raw(type, jid, nick, text, True)

def true_age(type, jid, nick, text):
	true_age_raw(type, jid, nick, text, None)

def true_age_raw(type, jid, nick, text, xtype):
	text = text.rstrip().split('\n')
	llim = 10
	if len(text) > 1:
		try: llim = int(text[1])
		except: llim = GT('age_default_limit')
	text = text[0]
	if not text: text = nick
	if llim > GT('age_max_limit'): llim = GT('age_max_limit')
	real_jid = cur_execute_fetchone('select jid from age where room=%s and (nick=%s or jid=%s) order by -time,status',(jid,text,text.lower()))
	if not real_jid:
		text = '%%%s%%' % text.lower()
		real_jid = cur_execute_fetchone('select jid from age where room=%s and (no_case_nick ilike %s or jid ilike %s) order by -time,status',(jid,text,text))
	try:
		if xtype: sbody = cur_execute_fetchmany('select * from age where room=%s and jid=%s order by -time,status',(jid,real_jid[0]),llim)
		else:
			t_age = cur_execute_fetchone('select sum(age) from age where room=%s and jid=%s',(jid,real_jid[0]))
			sbody = cur_execute_fetchone('select * from age where room=%s and jid=%s order by -time,status',(jid,real_jid[0]))
			sbody = [sbody[:4] + t_age + sbody[5:]]
	except: sbody = None
	if sbody:
		msg = L('I see:','%s/%s'%(jid,nick))
		for cnt, tmp in enumerate(sbody):
			if tmp[5]: r_age = tmp[4]
			else: r_age = int(time.time()) - tmp[3] + tmp[4]
			if xtype: msg += '\n%s. %s' % (cnt + 1, tmp[1])
			else: msg += ' %s' % tmp[1]
			msg += '\t%s, ' % un_unix(r_age)
			if tmp[5]:
				if tmp[6]: msg += L('%s %s ago','%s/%s'%(jid,nick)) % (tmp[6], un_unix(int(time.time() - tmp[3])))
				else: msg += L('Leave %s ago','%s/%s'%(jid,nick)) % un_unix(int(time.time() - tmp[3]))
				t7sp = tmp[7].split('\r')[0]
				if t7sp.count('\n') > 3:
					stat = t7sp.split('\n', 4)[4]
					if stat: msg += ' (%s)' % stat
				elif t7sp: msg += ' (%s)' % t7sp
				if '\r' in tmp[7]: msg += ', %s %s' % (L('Client:','%s/%s'%(jid,nick)),' // '.join(tmp[7].split('\r')[-1].split(' // ')[:-1]))
			else: msg += L('Is here: %s','%s/%s'%(jid,nick)) % un_unix(int(time.time() - tmp[3]))
			if not xtype: msg = msg.replace('\t', ' - ')
	else: msg = L('Not found!','%s/%s'%(jid,nick))
	send_msg(type, jid, nick, msg)

def seen(type, jid, nick, text):
	seen_raw(type, jid, nick, text, None)

def seen_split(type, jid, nick, text):
	seen_raw(type, jid, nick, text, True)

def seen_raw(type, jid, nick, text, xtype):
	text = text.rstrip().split('\n')
	llim = GT('age_default_limit')
	if len(text)>1:
		try: llim = int(text[1])
		except: llim = GT('age_default_limit')
	text = text[0]
	if not text: text = nick
	if llim > GT('age_max_limit'): llim = GT('age_max_limit')
	real_jid = cur_execute_fetchone('select jid from age where room=%s and (nick=%s or jid=%s) order by status,-time',(jid,text,text.lower()))
	if not real_jid:
		textt = '%%%s%%' % text.lower()
		real_jid = cur_execute_fetchone('select jid from age where room=%s and (no_case_nick ilike %s or jid ilike %s) order by status,-time',(jid,textt,textt))
	if real_jid:
		if xtype: sbody = cur_execute_fetchmany('select * from age where room=%s and jid=%s order by status,-time',(jid,real_jid[0]),llim)
		else: sbody = [cur_execute_fetchone('select * from age where room=%s and jid=%s order by status,-time',(jid,real_jid[0]))]
	else: sbody = None
	if sbody:
		msg = L('I see:','%s/%s'%(jid,nick))
		for cnt, tmp in enumerate(sbody):
			if xtype: msg += '\n%s. ' % (cnt+1)
			else: msg += ' '
			if text != tmp[1]: msg += L('%s (with nick: %s)','%s/%s'%(jid,nick)) % (text,tmp[1])
			else: msg += tmp[1]
			if tmp[5]:
				if tmp[6]: msg += ' - ' + L('%s %s ago','%s/%s'%(jid,nick)) % (tmp[6], un_unix(int(time.time() - tmp[3])))
				else: msg += ' - ' + L('Leave %s ago','%s/%s'%(jid,nick)) % un_unix(int(time.time() - tmp[3]))
				t7sp = tmp[7].split('\r')[0]
				if t7sp.count('\n') > 3:
					stat = t7sp.split('\n',4)[4]
					if stat: msg += ' (%s)' % stat
				elif t7sp: msg += ' (%s)' % t7sp
				if '\r' in tmp[7]: msg += ', %s %s' % (L('Client:','%s/%s'%(jid,nick)),' // '.join(tmp[7].split('\r')[-1].split(' // ')[:-1]))
			else: msg += ' - '+ L('Is here: %s','%s/%s'%(jid,nick)) % un_unix(int(time.time()-tmp[3]))
	else: msg = L('Not found!','%s/%s'%(jid,nick))
	send_msg(type, jid, nick, msg)

def seenjid(type, jid, nick, text):
	seenjid_raw(type, jid, nick, text, None)

def seenjid_split(type, jid, nick, text):
	seenjid_raw(type, jid, nick, text, True)

def seenjid_raw(type, jid, nick, text, xtype):
	text = text.rstrip().split('\n')
	llim = GT('age_default_limit')
	if len(text)>1:
		try: llim = int(text[1])
		except: llim = GT('age_default_limit')
	text = text[0]
	ztype = None
	if not text: text = nick
	if llim > GT('age_max_limit'): llim = GT('age_max_limit')
	real_jid = cur_execute_fetchall('select jid from age where room=%s and (nick ilike %s or jid ilike %s) group by jid,status,time order by status,-time',(jid,text,text.lower()))
	if not real_jid:
		txt = '%%%s%%' % text.lower()
		real_jid = cur_execute_fetchall('select jid from age where room=%s and (no_case_nick ilike %s or jid ilike %s) group by jid,status,time order by status,-time',(jid,txt,txt))
	sbody = []
	if real_jid:
		for rj in real_jid:
			if xtype: tmpbody = cur_execute_fetchmany('select * from age where room=%s and jid=%s order by status, jid',(jid,rj[0]),llim)
			else: tmpbody = [cur_execute_fetchone('select * from age where room=%s and jid=%s order by status',(jid,rj[0]))]
			if tmpbody:
				for t in tmpbody:
					if t not in sbody: sbody.append(t)
	if sbody:
		ztype = True
		msg = L('I saw %s:','%s/%s'%(jid,nick)) % text
		for cnt, tmp in enumerate(sbody):
			msg += '\n%s. %s (%s)' % (cnt + 1, tmp[1], tmp[2])
			if tmp[5]:
				if tmp[6]: msg += '\t' + L('%s %s ago','%s/%s'%(jid,nick)) % (tmp[6], un_unix(int(time.time() - tmp[3])))
				else: msg += '\t' + L('Leave %s ago','%s/%s'%(jid,nick)) % un_unix(int(time.time() - tmp[3]))
				t7sp = tmp[7].split('\r')[0]
				if t7sp.count('\n') > 3:
					stat = t7sp.split('\n', 4)[4]
					if stat: msg += ' (%s)' % stat
				elif t7sp: msg += ' (%s)' % t7sp
				if '\r' in tmp[7]: msg += ', %s %s' % (L('Client:','%s/%s'%(jid,nick)), tmp[7].split('\r')[-1])
			else: msg += '\t' + L('Is here: %s','%s/%s'%(jid,nick)) % un_unix(int(time.time() - tmp[3]))
			if not xtype: msg = msg.replace('\t', ' - ')
	else: msg = L('Not found!','%s/%s'%(jid,nick))
	if type == 'groupchat' and ztype:
		send_msg(type, jid, nick, L('Send for you in private','%s/%s'%(jid,nick)))
		send_msg('chat', jid, nick, msg)
	else: send_msg(type, jid, nick, msg)

global execute

execute = [(3, 'age', true_age, 2, L('Show age of jid in conference.')),
	 (3, 'age_split', true_age_split, 2, L('Show age of jid in conference splitted by nicks.')),
	 (3, 'seen', seen, 2, L('Show time of join/leave.')),
	 (3, 'seen_split', seen_split, 2, L('Show time of join/leave splitted by nicks.')),
	 (3, 'agestat', true_age_stat, 2, L('Show age statistic for conference.')),
	 (7, 'seenjid', seenjid, 2, L('Show time of join/leave + jid.')),
	 (7, 'seenjid_split', seenjid_split, 2, L('Show time of join/leave + jid splitted by nicks.'))]
