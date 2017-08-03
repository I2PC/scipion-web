 /*****************************************************************************
 *
 * Authors:    Adrian Quintana (aquintana@cnb.csic.es)
 * 			   Jose Gutierrez (jose.gutierrez@cnb.csic.es)
 *
 * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307  USA
 *
 *  All comments concerning this program package may be sent to the
 *  e-mail address 'scipion@cnb.csic.es'
 *
 ******************************************************************************/
/******************************************************************************
 * DESCRIPTION:
 * 
 * Methods used in the showj_gallery template 
 * 
 * METHODS LIST:
 * 
 * function initRenderFunction(labelToRender)
 * -> Initialize render function on all images. 
 * 	  Add renderFunction parameter and any other extra parameter to src attribute in image
 * 
 * function initializeGoToEvents()
 * -> Initialize events for Goto textfield
 * 	  Goto textfield allows to select any image in the gallery
 * 
 * function updateSelection()
 * -> Select image set in the Goto textfield and scroll to the image
 * 
 * function initializeImageEvents(hasEnabledColumn)
 * -> Initialize following hover and click events for images:
 *  	On hover Single enabled/disabled tool (red cross). Show enabled/disabled image and title on hover
 *  	On hover Multiple selection tool
 *  	On click Single selection and scpecial key controls (ctrl, shift, single click)
 *    
 * function initializeWindowLoadEvents()
 * -> Initialize events on window load.
 * 	  If manual col & row mode is set it updates main container dimensions
 * 
 * function multipleEnableDisableImage(mode)
 * -> Enables/disable a set of image. (actually the metadata row)
 *    Mode can be enable or disable
 * 
 * function enableDisableImage(element, enableDisable)
 * -> Enables/disable a single image.
 *    Mode can be enable or disable
 *    
 * function multipleSelect(mode)
 * -> Select a set of images
 *    Mode can be all, from (i.e. from the image that triggered the event until the end)
 *    or to (i.e. from the beginning until the image that triggered the event)     
 ******************************************************************************/

 /** METHODS ******************************************************************/
function initRenderFunction(labelToRender){
	renderFunc=jsonTableLayoutConfiguration.columnsLayout[labelToRender].renderFunc
	extraRenderFunc=jsonTableLayoutConfiguration.columnsLayout[labelToRender].extraRenderFunc
	
	if (renderFunc!=""){ 
		$(".tableImages").each(function(){
		   	var newSrc = $(this).data("real_src").replace(/(renderFunc=).*?(&)/,'$1' + renderFunc + '$2');
		   	if (extraRenderFunc!=""){newSrc = newSrc.concat("&"+extraRenderFunc)}
			$(this).data("real_src", newSrc);
	   	})
	}
}

function initializeGoToEvents(){
	$('#id_goto').click(function(){
		updateSelection();	
	});
	
	$('#id_goto').change(function(){
		updateSelection();
	});
		
	$('#id_goto').keyup(function(e){
		var code = e.keyCode || e.which; 
		  	if (code  == 13) {               
		  		updateSelection();
		  	}
	});	 
}

function updateSelection(){
	$(".img_container").each(function(){
		$(this).removeClass('image_selected')
	});
	selectedElement=$("#img_container___"+ (parseInt($('#id_goto').val())-1))
	selectedElement.addClass("image_selected")

    var container = $('#grid_section')

	var top = $(selectedElement).position().top - $(container).padding().top - $(container).position().top + $(container).scrollTop();

	$(container).scrollTop(top)
}

function initializeImageEvents(hasEnabledColumn){

	if (hasEnabledColumn){	
		//Hover on multiple selection tool	
		var hiConfig = {
	        sensitivity: 3, // number = sensitivity threshold (must be 1 or higher)
	        interval: 300, // number = milliseconds for onMouseOver polling interval
	        timeout: 800, // number = milliseconds delay before onMouseOut
	        over: function(e) {
	        	if ($(this).hasClass("image_selected") 
	        			&& $("#multipleSelectionTool").css('display')!="block"){
	        		var hoverElement = $(this).attr("id")
										
					$("#multipleSelectionTool").css('left',e.pageX)
					$("#multipleSelectionTool").css('top',e.pageY)
					$("#multipleSelectionTool").data('img_container_id',hoverElement)
					$("#multipleSelectionTool").fadeIn('slow')
				}
	        }, // function = onMouseOver callback (REQUIRED)
	        out: function() { 
	        	if ($(this).hasClass("image_selected") 
	        			&& hoverElement == $(this).attr("id")){
//					$("#multipleSelectionTool").fadeOut('slow')
				}
	        } // function = onMouseOut callback (REQUIRED)
	    }	
		
	$(".img_container").hoverIntent(hiConfig)
	}
	
	//Selection tool
	$(".img_container").click(
		function(e){
			var element_id = parseInt($(this).attr("id").split("___")[1]);

			if (e.shiftKey){
				var prev_element_id = parseInt($('#id_goto').val())
				
				if (prev_element_id < element_id){
					var initialIndex = prev_element_id
					var endIndex = element_id
				}
				else{
					initialIndex = element_id
					endIndex = prev_element_id
				}
				
				for (var x=initialIndex; x<=endIndex; x++){
					var id = "img_container___" + x
					$("#"+id).addClass("image_selected")
					
				}
			}
			else{
				if (!e.ctrlKey && !e.metaKey){
					$(".img_container").each(function(){
						$(this).removeClass('image_selected')
					});	
				}
				$("#img_container___"+element_id).toggleClass("image_selected")
				
			}
			$('#id_goto').val(element_id);
			
			/* Update the selected session list */
			replaceList('selected', getListSelectedItems('gallery'))
		})	
}

function initializeWindowLoadEvents(){
	$(window).load(function(){
		if ($("#id_colRowMode").val() == 'On' && $("#id_mode").val() == 'gallery'){
			updateMainContainerDim($("#id_cols").val())
		}
	})
}

function multipleEnableDisableImage(mode){
	$(".image_selected").each(function(){
		var elm = $(this).find(".enabledGallery");
		var id = $(this).attr("id");
		
		switch(mode){
			case 'enable':
				if(elm.hasClass('selected')){
					// Update the session list
					updateListSession(id, "enabled", "gallery")
				}
	
				enableDisableImage(elm, 'enable')
				elm.fadeOut('fast')
				break;
				
			case 'disable':
				if(!elm.hasClass('selected')){
					// Update the session list
					updateListSession(id, "enabled", "gallery")
				}
				
				enableDisableImage(elm, 'disable')
				elm.fadeIn('fast')
				break;
		}
	});
}

function enableDisableImage(element, enableDisable){
	if (enableDisable=='enable'){
		$(element).removeClass("selected")
	} else if (enableDisable=='disable'){
		$(element).addClass("selected")
	} else{
		$(element).toggleClass("selected")
	}
	
	if ($(element).hasClass("selected")){
		var element_value = 0
	} else {
		var element_value = 1
	}
}

function multipleSelect(mode){
	var element_id = parseInt($("#multipleSelectionTool").data('img_container_id').split("___")[1]);
	$(".img_container").each(function(){
		if(!$(this).hasClass("image_selected")){
			
			// Update the session list
			updateListSession($(this).attr("id"), "selected", "gallery")
			
			if (mode=='all' 
				|| (mode=='from' && $(this).attr('id').split("___")[1]>element_id) 
				|| (mode=='to' && $(this).attr('id').split("___")[1]<element_id)) {
				$(this).addClass("image_selected")
			}	
		}
		
	})
}

