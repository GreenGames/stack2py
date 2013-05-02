import urllib2
import zlib
import json
import pprint, webbrowser
from urllib import urlencode

__version__ = "0.1r3"
api_url = 'http://api.stackexchange.com/2.1/'
auth_url = 'https://stackexchange.com/oauth/dialog'

def make_proxy(proxy=None):
    '''Allows for connection through proxy'''
    proxy = urllib2.ProxyHandler(proxy)
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
    return True

def make_auth_proxy(proxy=None):
    '''Allows for connection through authenticated proxy'''
    proxy = urllib2.ProxyHandler(proxy)
    auth = urllib2.HTTPBasicAuthHandler()
    opener = urllib2.build_opener(proxy, auth)
    urllib2.install_opener(opener)

def make_url(base,kargs={},**kwargs):
    '''creates a url from base and keywords'''
    kwargs.update(kargs)
    return '%s?%s' %(base,urlencode(kwargs))

def get_dict(url):
    '''Returns the dictionary of the response from url'''
    data = urllib2.urlopen(url).read()
    return json.loads(zlib.decompress(data, 15 + 32))

def get_sites():
    '''Returns the name:api site name of all sites on SE'''
    sites = {}
    url = make_url(api_url+'\sites')
    dic = get_dict(url)
    for s in dic['items']:
        sites[s['name']] = Site(s['api_site_parameter'])
        sites[s['name']].get_info(s)
    return sites

def authenticate():
    '''Not fully implemented Don't use!!'''
    scope = "write_access,private_info,read_inbox"
    url = make_url(auth_url,client_id=1325,
                   scope=scope,response_type='code',
                   redirect_uri='https://stackexchange.com/oauth/login_success')
    webbrowser.open(url)

class Base:
    """ The base class for all the other classes """
    def __init__(self, uid, site, link):
        self.uid = uid
        self.site = site
        self.api_link = link
    def __repr__(self):
        return "{0} ID: {1}".format(self.__class__.__name__, self.uid)

    def set_args(self, dic):
        for key in dic:
            setattr(self,key,dic[key])

    def get_info(self,*args,**kwargs):
        if not args:
            url = make_url(self.api_link, kargs=kwargs,site=self.site)
            print url
            dic = get_dict(url)
            self.set_args(dic['items'][0])

        elif isinstance(args[0],dict):
            try:
                dic = args[0]
                self.set_args(dic)
            except KeyError:
                print 'Invaluid dictionary given'
                raise
        else:
            raise AttributeError('Invalid arguments')

class Site(Base):
    def __init__(self,site):
        self.site = site
        self.questions = []
        self.api_link = api_url+'info'

    def __repr__(self):
        return 'Site: '+ self.site

    def get_questions(self,**kwargs):
        url = make_url(api_url+'questions',kargs=kwargs,
                       site=self.site,filter='withbody')
        dic = get_dict(url)
        self.questions = [Question(q['question_id'],self.site)
                            for q in dic['items']]
        for i in range(len(self.questions)):
            self.questions[i].get_info(dic['items'][i])

class Post(Base):
    """ A post (Question Or Answer) """
    def __init__(self, uid, site, link):
        Base.__init__(self, uid, site, link)
        self.comments = []

    def set_args(self, dic):
        for key in dic:
            setattr(self,key,dic[key])
        if hasattr(self,'owner') and \
           self.owner['user_type'] in ('registered','moderator'):
            user = User(self.owner['user_id'],self.site)
            user.get_info(self.owner)
            self.owner = user

    def get_comments(self):
        url = make_url(self.api_link+'/comments',
                       site=self.site,filter='withbody')
        dic = get_dict(url)
        for comment in dic['items']:
            c = Comment(comment['comment_id'],self.site)
            c.get_info(comment)
            self.comments.append(c)

class Question(Post):
    def __init__(self, uid, site):
        Post.__init__(self, uid, site, api_url+"questions/{0}".format(uid))
        self.answers = []

    def get_answers(self):
        url = make_url(self.api_link+'/answers',
                       site=self.site,filter='withbody')
        dic = get_dict(url)
        for answer in dic['items']:
            a = Answer(answer['answer_id'],self.site)
            a.get_info(answer)
            self.answers.append(a)


class Answer(Post):
    def __init__(self, uid, site):
        Post.__init__(self, uid, site, api_url+'answers/'+str(uid))


class Comment(Base):
    def __init__(self, uid, site):
        Base.__init__(self, uid, site, api_url+'comments/'+str(uid))

    def set_args(self, dic):
        for key in dic:
            setattr(self,key,dic[key])
        if hasattr(self,'owner') and \
           self.owner['user_type'] in ('registered','moderator'):
            user = User(self.owner['user_id'],self.site)
            user.get_info(self.owner)
            self.owner = user

class Badge(Base):
    def __init__(self, uid, site):
        Base.__init__(self, uid, site, api_url+'badges/'+str(uid))

    def set_args(self, dic):
        for key in dic:
            setattr(self,key,dic[key])
        if hasattr(self,'owner') and \
           self.owner['user_type'] in ('registered','moderator'):
            user = User(self.owner['user_id'],self.site)
            user.get_info(self.owner)
            self.owner = user

class Tag(Base):
    def __init__(self, uid, site):
        Base.__init__(self, uid, site, api_url+'tags/'+str(uid))

class User(Base):
    def __init__(self, uid, site):
        Base.__init__(self, uid, site, api_url+'users/'+str(uid))

