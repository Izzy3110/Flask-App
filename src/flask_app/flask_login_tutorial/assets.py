"""Create and bundle CSS and JS files."""
from flask_assets import Bundle, Environment 
from Crypto.PublicKey import RSA
import os
import sys
from dotenv import load_dotenv

def recreate_key():
    load_dotenv()
    key_size = 4096
    key_filename = "rsa_key.bin"
    key_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), key_filename)
    algo = "scryptAndAES128-CBC"
    pkcs_int = 8
    secret_code = os.environ.get("APP_PASSWORD", "UnguessablePW123!")

    pubkey_filename = os.path.basename(key_filename).rstrip(".bin") + ".pub"
    pubkey_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), pubkey_filename)

    #if not os.path.isfile(key_filepath):
    print(">> CREATEING NEW RSA...", end='')
    key = RSA.generate(key_size)
    encrypted_key = key.export_key(
        passphrase=secret_code, 
        pkcs=pkcs_int,
        protection=algo
    )

    file_out = open(key_filepath, "wb")
    file_out.write(encrypted_key)
    file_out.close()
    with open(pubkey_filepath, "w") as pubkey_f:
        pubkey_f.write(key.publickey().export_key("PEM").decode("utf-8"))
        pubkey_f.close()
    print("done")
    # else:
    #     encoded_key = open(key_filepath, "rb").read()
    #     key = RSA.import_key(encoded_key, passphrase=secret_code)
    # 
    #     with open(pubkey_filepath, "w") as pubkey_f:
    #         pubkey_f.write(key.publickey().export_key("PEM").decode("utf-8"))
    #         pubkey_f.close()


def compile_static_assets(app):
    """Configure static asset bundles."""

    recreate_key()
    
    
    
    assets = Environment(app)
    Environment.auto_build = True
    Environment.debug = False
    # Stylesheets Bundles
    account_less_bundle = Bundle(
        "src/less/account.less",
        filters="less,cssmin",
        output="dist/css/account.css",
        extra={"rel": "stylesheet/less"},
    )
    dashboard_less_bundle = Bundle(
        "src/less/dashboard.less",
        filters="less,cssmin",
        output="dist/css/dashboard.css",
        extra={"rel": "stylesheet/less"},
    )
    # JavaScript Bundle
    js_bundle = Bundle("src/js/main.js", filters="jsmin", output="dist/js/main.min.js")
    # Register assets
    assets.register("account_less_bundle", account_less_bundle)
    assets.register("dashboard_less_bundle", dashboard_less_bundle)
    assets.register("js_all", js_bundle)
    # Build assets
    account_less_bundle.build()
    dashboard_less_bundle.build()
    js_bundle.build()
