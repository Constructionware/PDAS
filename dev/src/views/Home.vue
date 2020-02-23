<template>
  <div class="home">
    <p>The Worksman </p>
    <div>
      <p id="msg"> {{message.receive}}</p>
    </div>
    <div>
        <input type="text" id="auth" placeholder="Username" v-model.lazy="user.username"><br>
       <input type="text" id="msg" placeholder="Message" v-model="message.send.data"><br>
      <button @click="sendMessage">Send Message</button>
    </div>
    <div>
      <p v-if="message.warning">{{message.warning}}</p>
        <p v-if="message.info">{{message.info}}</p>
        <p v-if="message.success">{{message.success}}</p>
    </div>
   
  </div>
</template>

<script>
// @ is an alias to /src


export default {
  name: 'Home',
  components: {
    
  },
  data() {
    return{
      user: {
        username: null

      },
      
      message: {
        send: { 
          status: "ok"|"error",
          event: 'LOGIN',
          data: null
        },
        receive: null,
        info: null,
        success: null,
        warning: null
      }
    }
  },
  methods: {
    sendMessage(){
      const self = this;
      if ("WebSocket" in window) {
        self.message.info = 'Socket Support Available'
        var ws = new WebSocket("ws://" + location.hostname + ":3601/ws");

       
        ws.onopen = function() {

          self.message.info = 'Sending websocket data to the server';
          self.message.send.user = self.user
          ws.send(self.message.send);
        };
        ws.onmessage = function(server_response){
          console.log(server_response)
          self.message.receive = server_response.data;
        };
        ws.onclose = function() {
         
            self.message.info = 'Closing the websocket Connection.'
          
          
        };

      }else{
        self.message.warning = 'Sorry Socket Support is not available in your browser!'

      }
      

    },

  }

}
</script>
<style scoped>
#auth,#msg {
  margin-bottom: 15px;
  padding: 5px;
  border-bottom-left-radius: 5px;
  border-bottom-right-radius: 2px;

}
button {
  padding: 10px;
  color:darkblue ;
  background-color: dodgerblue;
}

</style>
