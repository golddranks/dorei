<%page args="
ua={
	'browser':{
		'name':None
	},
	'os':{
		'name':None
	},
},
static_dir='/static/'
"/><!DOCTYPE html>
<html lang="fi" class="${ua['browser']['name']} ${ua['os']['name']}">
<head>
	<link rel="stylesheet" type="text/css" href="${static_dir}default.css" media="screen" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="Content-type" content="text/html;charset=UTF-8">
	<%block name="head" />
	<!--[if lt IE 9]><script src="${static_dir}/html5shiv.js"></script><![endif]-->
	<title>ど例。Dorei.</title>
	<meta name="Description" content="Esimerkkejä suoraan animesta." />	
	<link href='http://fonts.googleapis.com/css?family=Lato:700' rel='stylesheet' type='text/css'>
	<link href='http://fonts.googleapis.com/css?family=Tauri' rel='stylesheet' type='text/css'>
	<script src="${static_dir}jquery-1.10.0.min.js"></script>
</head>
<body>
${self.body()}
<%block name="domloaded" />
</body>
</html>
