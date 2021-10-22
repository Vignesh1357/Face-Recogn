let intervalId=null;

function video(user, n){

        var capture = document.querySelector("#capture");
        var detect = document.querySelector("#detect");
        var vid = document.getElementById("#vid");
        var timer = document.getElementById("timer");
        var counter = document.getElementById("counter");

        let download_link = document.querySelector("#download-video");

        //Add aws creds here
        var albumBucketName = "";
        var bucketRegion = "";
        AWS.config.update({
          accessKeyId:"",
          secretAccessKey: "",
          region: bucketRegion,
        });

        var s3 = new AWS.S3({
          apiVersion: "2006-03-01",
          params: { Bucket: albumBucketName }
        });

        async function addVid(albumName, file, fileName) {
              console.log(fileName)
              if(n===1){
                var photoKey ='videos/'+ fileName
              }
              else{
                var photoKey ='detect_vids/'+ fileName
              }
                const params = {
                    Bucket: albumBucketName,
                      Key: photoKey,
                      Body: file
                }
                s3.putObject(params, function(err,data){
                    if(err){
                    alert(err)
                    return;
                    }
                    else{
                    counter.innerHTML='You can proceed further'
                    window.alert("Video Captured Successfully...")
                    }

                    clearInterval(intervalId);

                })
            }

        if (navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                video.srcObject = stream;
                var seconds = 15;
                let blobs_recorded = [];
                const media_recorder=new MediaRecorder(stream, { mimeType: 'video/webm' })

                media_recorder.addEventListener('dataavailable', function(e) {
                blobs_recorded.push(e.data);
                const file=new Blob(blobs_recorded, { type: 'video/webm' })
                const video_local = URL.createObjectURL(new Blob(blobs_recorded, { type: 'video/webm' }));

                addVid('videos',file,user)

               });

                media_recorder.start();


                function incrementSeconds() {

                    seconds -= 1;
                    timer.innerHTML=seconds
                    if(seconds===0){

                        timer.remove()
                        stop();
                    }
                    }
                intervalId = setInterval(incrementSeconds, 1000);
            })

            .catch(function (err0r) {
                  console.log("Something went wrong!");
            });

            function stop() {

                var stream = video.srcObject;
                var tracks = stream.getTracks();

                for (var i = 0; i < tracks.length; i++) {
                     var track = tracks[i];
                     track.stop();

                }

                video.srcObject = null;

                }
            }
    }

