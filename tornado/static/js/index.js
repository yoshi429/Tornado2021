// post_list
const openPostModal = postId => {
  document.getElementById(`post-modal-${postId}`)
    ?.classList.add("open-modal");
  console.log(postId);
};

const closePostModal = postId => {
  document.getElementById(`post-modal-${postId}`)
    ?.classList.remove("open-modal");
  console.log(postId);
};

// newpost
const openNewPostModal = () => {
  document.getElementById("new-post-modal").classList.add("open-modal");
  document.getElementById("plan-title").textContent = "";
  document.getElementById("plan-description").textContent = "";
};

const closeNewPostModal = () => {
  console.log(document.getElementById("new-post-modal").classList);
  document.getElementById("spot-edit-modal-1").classList.remove("open-modal");
  document.getElementById("spot-edit-modal-2").classList.remove("open-modal");
  document.getElementById("spot-edit-modal-3").classList.remove("open-modal");
  document.getElementById("spot-edit-modal-4").classList.remove("open-modal");
  document.getElementById("spot-edit-modal-5").classList.remove("open-modal");
  document.getElementById("new-post-modal").classList.remove("open-modal");
  document.getElementById("new-post-modal-content").classList.remove("stucked");
};

let spotCount = 0;
let editSpotId = null;

const openEditModal = _spotId => {
  const spotId = _spotId == null
    ? spotCount + 1
    : _spotId;
  document.getElementById("new-post-modal-content").classList.add("stucked");
  document.getElementById(`spot-edit-modal-${spotId}`).classList.add("open-modal");
  editSpotId = _spotId;

  // 現在の入力内容を取得
  const src = document.querySelector(`#spot-card-${spotId} .spot-img-top`)
    ?.src;
  const title = document.querySelector(`#spot-card-${spotId} .spot-card-title`)
    ?.textContent;
  const description = document.querySelector(`#spot-card-${spotId} .spot-card-description`)
    ?.textContent;
  // 入力内容をモーダルに反映

  document.getElementById(`spot-edit-modal-img-${spotId}`).src = src == null
    ? ""
    : src;
  document.getElementById(`spot-title-input-${spotId}`).value = title == null
    ? ""
    : title;
  document.getElementById(`spot-description-input-${spotId}`).value = description == null
    ? ""
    : description;
  // document.getElementById(`added-spot-${spotId}`)
};

const closeEditModal = spotId => {
  // モーダルを非表示
  document.getElementById("new-post-modal-content").classList.remove("stucked");
  document.getElementById(`spot-edit-modal-${spotId}`).classList.remove("open-modal");
  // 値をリセット
  document.getElementById(`spot-title-input-${spotId}`).value = "";
  document.getElementById(`spot-description-input-${spotId}`).value = "";
  document.getElementById(`spot-edit-modal-img-${spotId}`).src = "";
  document.getElementById(`spot-${spotId}-image`).src = "";
};

const completeEditModal = spotId => {
  if (spotCount > 5) {
    alert("スポットはこれ以上登録できません");
    return;
  }
  // モーダルの入力内容を取得
  const title = document.getElementById(`spot-title-input-${spotId}`).value;
  const description = document.getElementById(`spot-description-input-${spotId}`).value;
  const imgSrc = document.getElementById(`spot-edit-modal-img-${spotId}`).src;
  if (title == null || title === "") {
    alert("タイトルを入力してください");
    return;
  }
  if (imgSrc == null || imgSrc === "") {
    alert("画像をアップロードしてください");
    return;
  }

  // モーダルを非表示
  document.getElementById("new-post-modal-content").classList.remove("stucked");
  document.getElementById(`spot-edit-modal-${spotId}`).classList.remove("open-modal");

  // 新規追加か判定
  if (editSpotId == null) {
    spotCount += 1;
    // spot-cardを表示
    document.getElementById(`spot-card-${spotCount}`).classList.remove("not-added");
    document.querySelector(`#spot-card-${spotCount} .spot-card-title`).textContent = title;
    document.querySelector(`#spot-card-${spotCount} .spot-card-description`).textContent = description;
    document.querySelector(`#spot-card-${spotCount} .spot-img-top`).src = imgSrc;
  } else {
    // spot-cardに反映
    document.querySelector(`#spot-card-${editSpotId} .spot-card-title`).textContent = title;
    document.querySelector(`#spot-card-${editSpotId} .spot-card-description`).textContent = description;
    document.querySelector(`#spot-card-${editSpotId} .spot-img-top`).src = imgSrc;
    // 編集終了
    editSpotId = null;
  }
};

// 編集/追加モーダルの画像プレビュー
const onSelectSpotImage = (e, spotId) => {
  if (e.files.length === 0) {
    return;
  }
  const imgUrl = URL.createObjectURL(e.files[0]);
  console.log(imgUrl);
  document.getElementById(`spot-edit-modal-img-${spotId}`).src = imgUrl;
  document.querySelector(`#spot-card-${spotId} .spot-img-top`).src = imgUrl;
};

// カテゴリ選択時の反映
const onSelectCategory = category => {
  document.getElementById("plan-category").value = category;
  document.getElementById(`${category}-category-button`).classList.add("selected");
  ["pets", "elderly", "wheelchair"].forEach(_category => {
    if (category === _category) {
      document.getElementById(`${_category}-category-button`).classList.add("selected");
      document.getElementById(`${_category}-category-button`).classList.add("selected");
    } else {
      document.getElementById(`${_category}-category-button`).classList.remove("selected");
      document.getElementById(`${_category}-category-button`).classList.remove("selected");
    }
  });
};

window.onload = () => {
  // 初期値の設定
  onSelectCategory("pets");
};
