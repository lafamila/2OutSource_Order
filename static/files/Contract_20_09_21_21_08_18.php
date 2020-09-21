<?php defined('BASEPATH') OR exit('No direct script access allowed');

/**
 * 계약관리
 * 
 * @package     NEXELL
 * @subpackage  Contract
 * @category    Controller
 * @author      MAFU Co.,Ltd. <mafuceo@mafu.kr>
 * @since       Version 1.3.8
 * @update      2019-01-15 00:00
 */
class Contract extends YN_Controller
{
    /**************************************************************************
     * 생성자
     */
    public function __construct()
    {
        parent::__construct();

        /* 리소스를 로딩합니다. */
        $this->load->model('Contract_model', 'm_contract');
        $this->load->model('File_model', 'm_file');
    }

    /**************************************************************************
     * 기본 페이지를 처리합니다.
     */
    public function index()
    {
        $this->contract();
    }

/* ######################################################################### */
/* # 계약관리(목록)                                                        # */
/* ######################################################################### */

    /**************************************************************************
     * 계약관리(목록) 페이지를 처리합니다.
     */
	public function contract()
	{
		// 화면에 전달할 데이터 변수
		$data = array();

        // 컨텐츠 제목을 지정합니다.
        $data['title'] = '계약 관리';

        // 코드 데이터를 조회합니다.
        $data['progrs_sttus_code_list'] = $this->m_common->get_code_list(array('s_parnts_code'=>'PROGRS_STTUS_CODE'));
        $data['prjct_ty_code_list'] = $this->m_common->get_code_list(array('s_parnts_code'=>'PRJCT_TY_CODE'));
        $data['dept_code_list'] = $this->m_common->get_code_list(array('s_parnts_code'=>'GOAL_DEPT_CODE'));
        $data['member_list'] = $this->m_common->get_member_list(array());
        $data['bcnc_list'] = $this->m_common->get_bcnc_list(array('s_bcnc_se_code' => 'S'));

        // 화면에 뷰를 출력합니다.
        $this->_view('contractManage', $data, TRUE);
    }
    
    /**************************************************************************
     * 계약 목록을 조회합니다.
     */
    public function ajax_get_contract_datatable() {

        // 데이터를 조회합니다.
        $params = $this->input->post();
        $result = $this->m_contract->get_contract_datatable($params);
        $result['summery'] = $this->m_contract->get_contract_summery($params);

        // 데이터를 반환합니다.
        exit($this->_json_encode(TRUE, $result));
    }

    /**************************************************************************
     * 계약 정보를 조회합니다.
     */
    public function ajax_get_contract()
    {
        // 데이터를 조회합니다.
        $params = $this->input->get();
        $result['data'] = $this->m_contract->get_contract($params);

        // 데이터를 반환합니다.
        exit($this->_json_encode(TRUE, $result));
    }
    public function ajax_get_biss()
    {
        // 데이터를 조회합니다.
        $params = $this->input->get();
        $result['data'] = $this->m_contract->get_biss($params);

        // 데이터를 반환합니다.
        exit($this->_json_encode(TRUE, $result));
    }

    /**************************************************************************
     * 계약 정보를 등록합니다.
     */
    public function ajax_insert_contract()
    {
        $params = $this->input->post();

        /* 업로드 파일을 처리합니다. */
        // $config['upload_path'] = APP_UPLOAD_PATH.'contract'.DIRECTORY_SEPARATOR;
        // // $config['allowed_types'] = 'jpg|png';
        // $upload = $this->_upload('tmplt_file', $config);
        // if (isset($upload['error'])) {
        //     exit($this->_json_encode(FALSE, array('error' => $upload['error'])));
        // }

        // 데이터를 등록합니다.
        // $params['img_url'] = '/uploads/template/'.$upload['file_name'];
        $status = $this->m_contract->insert_contract($params);

        // 데이터를 반환합니다.
        $result['message'] = $this->lang->line('complete_insert');
        $result['s_cntrct_sn'] = $status;
        exit($this->_json_encode(!empty($status), $result));
    }

    /**************************************************************************
     * 계약 정보를 수정합니다.
     */
    public function ajax_update_contract()
    {
        $params = $this->input->post();

        // 데이터를 수정합니다.
        $status = $this->m_contract->update_contract($params);

        // 데이터를 반환합니다.
        $result['message'] = $this->lang->line('complete_update');
        exit($this->_json_encode($status, $result));
    }
    
    public function ajax_update_author()
    {
        $params = $this->input->post();

        // 데이터를 수정합니다.
        $status = $this->m_contract->update_author($params);

        // 데이터를 반환합니다.
        $result['message'] = $this->lang->line('complete_update');
        exit($this->_json_encode($status, $result));
    }
    public function ajax_update_biss()
    {
        $params = $this->input->post();

        // 데이터를 수정합니다.
        $status = $this->m_contract->update_biss($params);

        // 데이터를 반환합니다.
        $result['message'] = $this->lang->line('complete_update');
        exit($this->_json_encode($status, $result));
    }

    /**************************************************************************
     * 계약을 마감합니다.
     */
    public function ajax_update_contract_complete()
    {
        $params = $this->input->post();

        // 데이터를 수정합니다.
        $status = $this->m_contract->update_contract_complete($params);

        // 데이터를 반환합니다.
        $result['message'] = $this->lang->line('complete_update');
        exit($this->_json_encode($status, $result));
    }

    /**************************************************************************
     * 계약 정보를 삭제합니다.
     */
    public function ajax_delete_contract()
    {
        $params = $this->input->post();

        // 데이터를 삭제합니다.
        $status = $this->m_contract->delete_contract($params);

        // 데이터를 반환합니다.
        $result['message'] = $this->lang->line('complete_delete');
        exit($this->_json_encode($status, $result));
    }
}
