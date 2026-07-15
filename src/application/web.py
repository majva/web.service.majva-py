import os
import importlib
import inspect
from pathlib import Path
from uvicorn import run
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html

from src.core.utils.config_reader import ConfigReader


class WebService:

    def __init__(self):
        self.config = ConfigReader()
        
        self.__app__ = FastAPI(
            title=self.config.get_app_name(),
            description=self.config.get_app_description(),
            version=self.config.get_app_version(),
            docs_url=None,  # Disable default docs
            redoc_url=None,  # Disable default redoc
        )

        # Add CORS middleware
        cors_config = self.config.get_cors_config()
        self.__app__.add_middleware(
            CORSMiddleware,
            allow_origins=cors_config.get('allow_origins', ["*"]),
            allow_credentials=cors_config.get('allow_credentials', True),
            allow_methods=cors_config.get('allow_methods', ["*"]),
            allow_headers=cors_config.get('allow_headers', ["*"]),
        )

        # Auto-discover and register controllers
        self._register_controllers()

        @self.__app__.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            return get_swagger_ui_html(
                openapi_url=self.__app__.openapi_url,
                title=f"{self.__app__.title} - Swagger UI",
                oauth2_redirect_url="/docs/oauth2-redirect",
                swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
                swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
                swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
            )
        
    def _register_controllers(self):
        """
        Automatically discover and register all controllers in the application layer.
        Controllers should be in folders under src/application/ and have a *_controller.py file.
        """
        # Get the current application directory
        current_dir = Path(__file__).parent
        registered_controllers = []

        # Scan for controller directories
        for item in current_dir.iterdir():
            if item.is_dir() and not item.name.startswith('__'):
                controller_file = item / f"{item.name}_controller.py"
                
                if controller_file.exists():
                    try:
                        # Import the controller module
                        module_path = f"src.application.{item.name}.{item.name}_controller"
                        controller_module = importlib.import_module(module_path)
                        
                        # Find the controller class (should end with 'Controller')
                        controller_class = None
                        for name, obj in inspect.getmembers(controller_module):
                            if (inspect.isclass(obj) and 
                                name.endswith('Controller') and 
                                obj.__module__ == controller_module.__name__):
                                controller_class = obj
                                break
                        
                        if controller_class:
                            # Create controller instance
                            controller_instance = controller_class()
                            
                            # Get the router from the controller
                            if hasattr(controller_instance, 'api'):
                                router = controller_instance.api()
                                
                                # Create route prefix from controller name (lowercase)
                                api_prefix = self.config.get_api_prefix()
                                route_prefix = f"{api_prefix}/{item.name.lower()}"
                                
                                # Register the router
                                self.__app__.include_router(router, prefix=route_prefix)
                                registered_controllers.append(item.name)
                            else:
                                print(f"Controller {item.name} missing 'api()' method")
                        else:
                            print(f"No controller class found in {item.name}")
                            
                    except Exception as e:
                        print(f"Error registering controller {item.name}: {str(e)}")

        if not registered_controllers:
            print("No controllers were registered automatically")
        else:
            print(f"Successfully registered {len(registered_controllers)} controllers: {', '.join(registered_controllers)}")

    def start(self):
        run(
            self.__app__,
            host=self.config.get_server_host(),
            port=self.config.get_server_port(),
            # log_level="info",
        )

