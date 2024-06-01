if(TRUE)
               checkgitversion("${CheckGitSetup_REPOSITORY_PATH}"  "${CheckGitSetup_TEMPLATE_FILE}"  "${CheckGitSetup_OUTPUT_FILE}"  "${CheckGitSetup_INCLUDE_HEADER}")

               checkgitversion("${CheckGitSetup_REPOSITORY_PATH}"	"${CheckGitSetup_TEMPLATE_FILE}"	"${CheckGitSetup_OUTPUT_FILE}"	"${CheckGitSetup_INCLUDE_HEADER}")

               checkgitversion(${CheckGitSetup_REPOSITORY_PATH}  ${CheckGitSetup_TEMPLATE_FILE}  ${CheckGitSetup_OUTPUT_FILE}  ${CheckGitSetup_INCLUDE_HEADER})

               checkgitversion(${CheckGitSetup_REPOSITORY_PATH}	${CheckGitSetup_TEMPLATE_FILE}	${CheckGitSetup_OUTPUT_FILE}	${CheckGitSetup_INCLUDE_HEADER})
endif()
