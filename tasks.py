from __future__ import absolute_import
import facebook
import tweepy
import logging
import urllib
import uuid

from stark.models.schema import ProductSchema, CustomerSocmedAccountTokenSchema

from .utils import StringUtils
from sociale.celery import app

TWEET_HEADLINE_LENGTH = 115
logger = logging.getLogger(__name__)


@app.task
def post_fb(params):
	''' post to facebook task '''
	logger.debug('FacebookTask: post to facebook')
	logger.debug(params)
	try:
		# params
		fb_account = CustomerSocmedAccountTokenSchema().load(params['fb_account']).data
		headline = params['headline']
		product = ProductSchema().load(params['product']).data
		product_page = params['product_page']
		
		# post to FB
		logger.debug('FacebookTask: account  : %s' % fb_account['social_name'])
		logger.debug('FacebookTask: headline : %s' % headline)

		# build graph api
		ACCESS_TOKEN = fb_account['token']
		graph = facebook.GraphAPI(access_token=ACCESS_TOKEN)

		# set headline
		message = "%s %s" % (headline, product_page)

		# build post params
		attachment =  {
			'name': product['name'],
			'link': product_page,
			'description': product['description'],
			'picture': product['image']
		}
		# post it
		graph.put_wall_post(message=message, attachment=attachment)
		
		return True

	except Exception, error:
		logger.exception(error);
		return False

@app.task
def post_twitter(params):
	''' post to twitter task '''
	logger.debug('TwitterTask: post to twitter')
	logger.debug(params)
	try:
		# params
		twitter_account = CustomerSocmedAccountTokenSchema().load(params['twitter_account']).data
		headline = params['headline']
		product = ProductSchema().load(params['product']).data
		product_page = params['product_page']
		
		# post to Twitter
		logger.debug('TwitterTask: account  : %s' % twitter_account['social_name'])
		
		# download image
		temp_path = '/tmp/'
		image_path = '%s/%s.jpg' % (temp_path, uuid.uuid4())
		urllib.urlretrieve(product['image'], image_path)

		# post to twitter
		social_media = twitter_account['social_media']
		CONSUMER_KEY = social_media['consumer_key']
		CONSUMER_SECRET = social_media['consumer_secret']
		ACCESS_TOKEN = twitter_account['token']
		ACCESS_TOKEN_SECRET = twitter_account['secret']

		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
		api = tweepy.API(auth)

		headline = StringUtils.ellipsis(headline, length=TWEET_HEADLINE_LENGTH, suffix='')
		logger.debug('TwitterTask: headline : %s' % headline)
		status = "%s %s" % (headline, product_page)
		
		# post it
		api.update_with_media(image_path, status=status)
		
		return True

	except Exception, error:
		logger.exception(error);
		return False
