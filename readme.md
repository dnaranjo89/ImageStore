## How to use the API
To use the API simply make a GET request to the following URL:

* Cached access `http://127.0.0.1:8000/images`

It is possible to force the server to check if there are changes in the sources and bring their content to the server.
* Force server to check updates `http://127.0.0.1:8000/images?f`

### Output formats
Beside the required JSON, the API also can be served with a HTML browsable interface. To select between formats use the sufixs `.api` and `.json`

Examples:
* `http://127.0.0.1:8000/images.api`
* `http://127.0.0.1:8000/images.json?f`

## Caching images
When the images are downloaded by first time they will be optimized and stored in the server.

Everytime a SCV file is fetched, the file is hashed and the hash is stored. It will be used to check whether the CSV file changed since the last time it was downloaded.

#### Assumptions
* If a CSV file is completely removed, the server will keep the entries in the DB for backup purposes. The entries can be removed from the database:
 * Removing all the entries from the CSV file (but leaving the file with header)
 * Removing the CSVFile entry from the database

## Compressing images
For the sake of example, the following are the weights of the default set of images with and without compresion
* Original set of images 10.8Mb
* Compressed set of images 2.33Mb **(Saving 78%)** 

## Logs
A log file is generated with the source errors to be submitted to the image supplier to fix them. The file is located in `logs/image_suppliers_log.txt` 

    ...
    [11/09/2015 10:38:39] INFO The image didn't pass the validation: ['The image has no title, which is required. (URL: https://avatars2.githubusercontent.com/u/11301498?v=3&s=200)']
    [11/09/2015 10:38:39] INFO The image didn't pass the validation: ['The image has no title, which is required. (URL: https://avatars2.githubusercontent.com/u/11301498?v=3&s=200)']
    [11/09/2015 10:38:39] INFO The image didn't pass the validation: ['The URL is not correctly formatted. Enter a valid URL (URL: asdsa)']
    ...

## Production server
I was setting up the production server with Heroku when I realized that it does not support storeing files in it's server. Currently the app generated stores the images in the server so it's not working properly.

The server is running, but it does not cache the images:
* https://quiet-wave-8914.herokuapp.com/images.json (The first time run it's a bit slower since it's a free account in Heroku and the server is sleeping when not used)

The solutions could be:
* Serving it from a VPS where you are free to store your content. But this option would requite more effort.
* Simply using a S3 (i.e. Amazon S3) to store the images.

_I'm not sure if setting the production server is something that is expected for me to do but if so, please let me know and I will gladly do it._
