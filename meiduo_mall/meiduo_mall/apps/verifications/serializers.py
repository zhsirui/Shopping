from rest_framework import serializers
from django_redis import get_redis_connection
from redis.exceptions import RedisError
import logging


logger = logging.getLogger('django')


class CheckImageCodeSerializer(serializers.Serializer):

    image_code_id = serializers.UUIDField()
    text = serializers.CharField(min_length=4, max_length=4)

    def validate(self, attrs):

        image_code_id = attrs['image_code_id']
        text = attrs['text']

        redis_conn = get_redis_connection("verify_codes")
        real_image_code = redis_conn.get('img_%s' % image_code_id)

        if real_image_code is None:
            raise serializers.ValidationError('无效的图片验证码')

        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)

        real_image_code = real_image_code.decode()
        if real_image_code.lower() != text.lower():
            raise serializers.ValidationError('图片验证码错误')

        mobile = self.context['view'].kwargs['mobile']
        redis_conn.get('send_flag_%s' )
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('发送短信次数过于频繁')

        return attrs