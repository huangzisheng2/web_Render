import { createApp } from 'vue'
import App from './App.vue'

// Vant 组件库
import { 
  Button, 
  Cell, 
  CellGroup, 
  Field, 
  Form, 
  Picker,
  Popup,
  DatePicker,
  TimePicker,
  Radio,
  RadioGroup,
  Loading,
  Toast,
  Notify,
  Dialog,
  NavBar,
  Card,
  Tag,
  Progress,
  Divider,
  Empty,
  Icon
} from 'vant'
import 'vant/lib/index.css'

const app = createApp(App)

// 注册 Vant 组件
app.use(Button)
app.use(Cell)
app.use(CellGroup)
app.use(Field)
app.use(Form)
app.use(Picker)
app.use(Popup)
app.use(DatePicker)
app.use(TimePicker)
app.use(Radio)
app.use(RadioGroup)
app.use(Loading)
app.use(Toast)
app.use(Notify)
app.use(Dialog)
app.use(NavBar)
app.use(Card)
app.use(Tag)
app.use(Progress)
app.use(Divider)
app.use(Empty)
app.use(Icon)

app.mount('#app')
