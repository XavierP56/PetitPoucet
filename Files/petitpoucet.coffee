app = angular.module 'petitpoucet', ["ui.bootstrap", "ui.grid", 'ui.grid.edit', 'ngResource', 'ui.ace', 'ui.layout']
    
app.controller "TraceCtrl", ($scope, $resource, $timeout, $location, $anchorScroll) ->  

    Refresh = $resource('/trace/refresh')
    Source = $resource('/trace/getFile',{},{do:{method:'POST'}})
    GetRecordStatus = $resource('/trace/getStatus')
    SetRecordStatus = $resource('/trace/setStatus/:status')
    FilterFiles = $resource('/trace/filterFiles',{},{do:{method:'POST'}})
    
    $scope.refresh = ()->
        Refresh.get {}, (list)->
            $scope.funcs = list.result
            $scope.files = list.files
    
    $scope.displaySrc = (idx, spath, sline)->
        $scope.curIdx = idx
        $scope.endIdx = $scope.funcs[idx].endidx
        
        $scope.curFile = spath
        Source.do {fPath:spath}, (result)->
            $scope.myFile = result.src
            $timeout ->
                $scope.editor.setReadOnly(true);
                $scope.editor.getSession().setMode("ace/mode/c_cpp");
                $scope.editor.gotoLine(sline)
            
    $scope.aceLoaded = (editor) ->
        $scope.editor = editor
        
    $scope.record = ()->
        $scope.myFile = ''
        $scope.curFile = ''
        $scope.funcs = []
        $scope.files = []
        SetRecordStatus.get { status: 1 }, (v)-> 
            $scope.status = v.res
    
    $scope.stop = ()->
        SetRecordStatus.get { status: 0 }, (v)-> 
            $scope.status = v.res
            $scope.refresh()
            
    $scope.scrollTo = (idx) ->
        key = "idx" + $scope.funcs[idx].endnum
        $timeout ->
            $location.hash(key)
            $anchorScroll()
        idx = $scope.funcs[idx].endidx
        $scope.displaySrc(idx, $scope.funcs[idx].from_src, $scope.funcs[idx].from_line)  
        
    
    $scope.chk = (idx) ->
        if ((idx > $scope.curIdx) && (idx < $scope.endIdx))
            return true
        return false
        
    $scope.filesToFilter = () ->
        FilterFiles.do  {filefilter:$scope.files}, (list) ->
            $scope.funcs = list.result
            $scope.files = list.files    
            
    # And start
    $scope.curFile = ''
    $scope.curIdx = 0
    GetRecordStatus.get {}, (v)->
        $scope.status = v.res
    $scope.refresh()

 
