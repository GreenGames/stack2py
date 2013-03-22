import urllib2, zlib, ast, pprint, webbrowser
from urllib import urlencode

__version__ = "0.1r02"
api_url = 'http://api.stackexchange.com/2.1/'
auth_url = 'https://stackexchange.com/oauth/dialog'

def make_proxy(proxy=None):
    '''Allows for connection through proxy'''
    proxy_support = urllib2.ProxyHandler(proxy)
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)
    return True
def make_auth_proxy(proxy=None):
    '''Allows for connection through authenticated proxy'''
    proxy = urllib2.ProxyHandler(proxy)
    auth = urllib2.HTTPBasicAuthHandler()
    opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
    urllib2.install_opener(opener)
    return True

def make_url(base,kargs={},**kwargs):
    '''creates a url from base and keywords'''
    kwargs.update(kargs)
    return '%s?%s' %(base,urlencode(kwargs))

def get_dict(url):
    '''Returns the dictionary of the response from url'''
    return ast.literal_eval(
        zlib.decompress(
            urllib2.urlopen(url).read(), 15 + 32)\
        .replace('false','False').replace('true','True'))

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
    '''Not fully implemented Don't use'''
    scope = "write_access,private_info,read_inbox"
    url = make_url(auth_url,client_id=1325,
                   scope=scope,response_type='code',
                   redirect_uri='https://stackexchange.com/oauth/login_success')
    webbrowser.open(url)

def get_token():
    '''Not fully implemented Don't use'''
    scope = "write_access,private_info,read_inbox"
    url = make_url(auth_url,client_id=1325,
               scope=scope,response_type='code',
               redirect_uri='https://stackexchange.com/oauth/login_success')
    print url
    page = urllib2.urlopen(url)

class Site:
    '''A site on SE network'''
    def __init__(self,site):
        self.site = site
        self.questions = []
    def __str__(self):
        return 'Site: '+ self.site
    __repr__ = __str__
        
    def get_questions(self,**kwargs):
        '''Loads questions into the class'''
        url = make_url(api_url+'questions',kargs=kwargs,
                       site=self.site,filter='withbody')
        dic = get_dict(url)
        self.questions = [Question(q['question_id'],self.site)
                            for q in dic['items']]
        for i in range(len(self.questions)):
            self.questions[i].get_info(dic['items'][i])

    def get_info(self,*args):
        '''Get information about site'''
        if not args:
            url = make_url(api_url+'info',site=self.site)
            dic = get_dict(url)
            self.set_args(dic['items'][0])

        elif isinstance(args[0],dict):
            try:
                dic = args[0]
                self.set_args(dic)
            except KeyError:
                print 'Invalid dictionary given'
                raise
        else:
            raise AttributeError('Invalid arguments')

    def set_args(self, dic):
        for key in dic:
            setattr(self,key,dic[key])

class Question:
    '''A Question on SE site'''
    def __init__(self,uid,site):
        self.question_id = uid
        self.site = site
        self.answers = []
        self.comment = []

    def __str__(self):
            return 'Question ID : '+str(self.question_id)
    __repr__ = __str__

    def set_args(self, dic):
        for key in dic:
            setattr(self,key,dic[key])
        if hasattr(self,'owner') and \
           self.owner['user_type'] in ('registered','moderator'):
            user = User(self.owner['user_id'],self.site)
            user.get_info(self.owner)
            self.owner = user
        else:
            user = User(None,self.site)
            user.get_info(self.owner)
            self.owner = user
            
    def get_info(self,*args,**kwargs):
        '''Get Information about the Question'''
        if not args:
            url = make_url(api_url+'questions/'+str(self.question_id),kargs=kwargs,site=self.site,filter='withbody')
            dic = get_dict(url)
            self.set_args(dic['items'][0])

        elif isinstance(args[0],dict):
            try:
                dic = args[0]
                self.set_args(dic)
            except KeyError:
                print 'Invalid dictionary given'
                raise
        else:
            raise AttributeError('Invalid arguments')

    def get_answers(self):
        '''Load answers into the class'''
        url = make_url(api_url+'questions/'+str(self.question_id)+'/answers',
                       site=self.site,filter='withbody')
        dic = get_dict(url)
        for answer in dic['items']:
            a = Answer(answer['answer_id'],self.site)
            a.get_info(answer)
            self.answers.append(a)

    def get_comments(self):
        '''Load comments into the class'''
        url = make_url(api_url+'questions/'+str(self.question_id)+'/comments',
                       site=self.site,filter='withbody')
        dic = get_dict(url)
        for comment in dic['items']:
            c = Comment(comment['comment_id'],self.site)
            c.get_info(comment)
            self.comments.append(c)
        
class Answer:
    '''Answer on SE site'''
    def __init__(self,uid,site):
        self.answer_id = uid
        self.site = site
    def __str__(self):
            return 'Answer ID : '+str(self.answer_id)
    __repr__ = __str__
    
    def set_args(self, dic):
        for key in dic:
            setattr(self,key,dic[key])
        if hasattr(self,'owner') and \
           self.owner['user_type'] in ('registered','moderator'):
            user = User(self.owner['user_id'],self.site)
            user.get_info(self.owner)
            self.owner = user
        else:
            user = User(None,self.site)
            user.get_info(self.owner)
            self.owner = user

    def get_info(self,*args,**kwargs):
        '''Get Information about the answer'''
        if not args:
            url = make_url(api_url+'answers/'+str(self.answer_id),kargs=kwargs,
                           site=self.site,filter='withbody')
            dic = get_dict(url)
            self.set_args(dic['items'][0])
            
        elif isinstance(args[0],dict):
            try:
                dic = args[0]
                self.set_args(dic)
            except KeyError:
                print 'Invalid dictionary given'
                raise
        else:
            raise AttributeError('Invalid arguments')

    def get_comments(self):
        '''Load comments into the class'''
        url = make_url(api_url+'questions/'+str(self.question_id)+'/comments',
                       site=self.site,filter='withbody')
        dic = get_dict(url)
        for comment in dic['items']:
            c = Comment(comment['comment_id'],self.site)
            c.get_info(comment)
            self.comments.append(c)
class User:
    '''User on SE site'''
    def __init__(self,uid,site):
        self.user_id = uid
        self.site = site    
    def __str__(self):
            return 'User No: '+str(self.user_id)
    __repr__ = __str__

    def set_args(self, dic):
        for key in dic:
            setattr(self,key,dic[key])
        
    def get_info(self,*args,**kwargs):
        '''Get Information about the User '''
        if not args:
            url = make_url(api_url+'users/'+str(self.user_id),kargs=kwargs,
                           site=self.site,filter='withbody')
            dic = get_dict(url)
            self.set_args(dic['items'][0])
        elif isinstance(args[0],dict):
            try:
                dic = args[0]
                self.set_args(dic)
            except KeyError:
                print 'Invalid dictionary given'
                raise
        else:
            raise AttributeError('Invalid arguments')

class Comment:
    '''Comment on SE site'''
    def __init__(self,uid,site):
        self.site = site
        self.comment_id = uid
    def __str__(self):
        return 'Comment ID: '+str(self.comment_id)
    __repr__ = __str__

    def set_args(self, dic):
        for key in dic:
            setattr(self,key,dic[key])
        if hasattr(self,'owner') and \
           self.owner['user_type'] in ('registered','moderator'):
            user = User(self.owner['user_id'],self.site)
            user.get_info(self.owner)
            self.owner = user
        else:
            user = User(None,self.site)
            user.get_info(self.owner)
            self.owner = user

    def get_info(self,*args,**kwargs):
        '''Get Information about the Comment'''
        if not args:
            url = make_url(api_url+'comments/'+str(self.comment_id),kargs=kwargs,
                           site=self.site,filter='withbody')
            dic = get_dict(url)
            self.set_args(dic['items'][0])
        elif isinstance(args[0],dict):
            try:
                dic = args[0]
                self.set_args(dic)
            except KeyError:
                print 'Invalid dictionary given'
                raise
        else:
            raise AttributeError('Invalid arguments')

