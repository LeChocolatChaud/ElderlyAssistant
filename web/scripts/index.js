$(function () {
  if (navigator.mediaDevices.getUserMedia) {
    const constraints = { audio: true };
    navigator.mediaDevices.getUserMedia(constraints).then(
      (stream) => {
        function register() {
          $.ajax({
            url: "/api/register",
            type: "GET",
            success: function (data) {
              $.cookie("id", data.id);
              $("button#talk-button").attr("disabled", false);
            },
          });
        }

        $("button#talk-button").attr("disabled", true);

        register();

        const context = new AudioContext();
        const recorder = new Recorder(context.createMediaStreamSource(stream));

        let animateTaskId = 0;

        $("button#send-button").attr("disabled", true);

        function stack(role, text) {
          switch (role) {
            case "bot":
              element = `<div class="message bot-message">${text}`;
              break;
            case "user":
              element = `<div class="message user-message">${text}`;
              break;
            default:
              throw new Error("Unsupported role.");
          }
          $("div#message-stacking").append(element);
        }
        function handleRecordButton() {
          if (recorder.recording) {
            recorder.stop();
            clearInterval(animateTaskId);
            $("button#talk-button").css({
              opacity: "1",
              border: "none",
            });
            $("img#button-image").attr("src", "assets/loading.gif");
            recorder.exportWAV((blob) => {
              const reader = new FileReader();
              reader.readAsDataURL(blob);
              reader.onloadend = () => {
                b64data = reader.result;
                if (!$.cookie("id")) {
                  alert("未登录！");
                  return;
                }
                $.ajax({
                  url: "/api/stt",
                  type: "POST",
                  headers: {
                    "Content-Type": "application/json",
                  },
                  data: JSON.stringify({
                    audio: b64data,
                    id: $.cookie("id"),
                  }),
                  success: function (data) {
                    recorder.clear();
                    $("input#input-text").val(data.text);
                    $("img#button-image").attr("src", "assets/microphone.png");
                    if (data.text != "") { 
                      $("button#send-button").attr("disabled", false);
                    } else {
                      $("button#send-button").attr("disabled", true);
                    }
                  },
                });
              };
            });
          } else {
            recorder.record();
            animateTaskId = setInterval(function () {
              $("button#talk-button").css({
                border: "4px solid #5361ff",
              });
              $("button#talk-button").animate({
                opacity: "-=0.6",
              });
              $("button#talk-button").animate({
                opacity: "+=0.6",
              });
            }, 1000);
          }
        }

        function handleSendButton() {
          stack("user", $("input#input-text").val());
          if (!$.cookie("id")) {
            alert("未登录！");
            return;
          }
          $.ajax({
            url: "/api/chat",
            type: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            data: JSON.stringify({
              message: $("input#input-text").val(),
              id: $.cookie("id"),
            }),
            success: function (data) {
              stack("bot", data.response);
            },
          });
          $("input#input-text").val("");
          $("button#send-button").attr("disabled", true);
        }

        function handleInputChange() {
          if ($("input#input-text").val() == "") {
            $("button#send-button").attr("disabled", true);
          } else {
            $("button#send-button").attr("disabled", false);
          }
        }

        $("button#talk-button").on("click", handleRecordButton);
        $("button#send-button").on("click", handleSendButton);
        $("input#input-text").on("input", handleInputChange);
      },
      () => {
        $("body").empty();
        alert("你禁止了麦克风授权，无法使用本应用！");
      }
    );
  } else {
    alert("浏览器不支持使用麦克风，请换用其他浏览器");
  }
});
