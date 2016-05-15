from pyramid.config import Configurator

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.add_static_view('static', 'docroot/static/', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('audio_kuuntele', '/audio_kuuntele')
    config.add_route('audio_dl', '/audio_dl')
    config.add_route('kohdan_ajastus', '/kohdan_ajastus')
    config.add_route('jakson_ajastus', '/jakson_ajastus')
    config.add_route('tallenna_ajastus', '/tallenna_ajastus')
    config.add_route('listaa_ajastukset', '/listaa_ajastukset')
    config.add_route('listaa_ajastukset_reverse', '/listaa_ajastukset_reverse')
    config.scan()
    return config.make_wsgi_app()
