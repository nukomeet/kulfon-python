require 'yaml'

ignore /\/data\/.*/
data = YAML.load_file('data/main.yml')

layout /.*html.erb/ => 'layouts/base.html.erb'

before 'index.html.erb' do
  @body_class = 'index'
  @widgets = data['widgets']
end