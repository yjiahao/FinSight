var Role;
(function (Role) {
    Role["admin"] = "Admin";
    Role["user"] = "User";
    Role["guest"] = "Guest";
})(Role || (Role = {}));
function checkAccess(role) {
    if (role === Role.admin) {
        console.log("Access granted to admin.");
    }
    else if (role === Role.user) {
        console.log("Access granted to user.");
    }
    else if (role === Role.guest) {
        console.log("Access granted to guest.");
    }
    else {
        console.log("Access denied.");
    }
}
checkAccess(Role.admin);
var myPet = "cat";
myPet = "turtle";
// pet = "hello";
// tsc test.ts
// node test.js
